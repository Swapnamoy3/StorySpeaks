document.addEventListener('DOMContentLoaded', () => {
    updateSliderDisplay('pitch');
    updateSliderDisplay('rate');
    updateSliderDisplay('volume');

    // Attach event listener to the upload button
    const uploadButton = document.getElementById("uploadButton");
    if (uploadButton) {
        uploadButton.addEventListener('click', uploadPDF);
    }
});

function updateSliderDisplay(type) {
    const display = document.getElementById(`${type}Display`);
    const slider = document.getElementById(type);
    if (display && slider) {
        display.textContent = slider.value;
    }
}

function onFileChange() {
    const fileInput = document.getElementById("pdfFile");
    const pdfIframe = document.getElementById("pdfIframe");
    const file = fileInput.files[0];

    if (file && file.type === "application/pdf") {
        pdfIframe.src = URL.createObjectURL(file);
    } else {
        pdfIframe.src = "";
    }
}

async function uploadPDF() {
    const fileInput = document.getElementById("pdfFile");
    const file = fileInput.files[0];

    if (!file) {
        showStatus("Please select a PDF file first.", "error");
        return;
    }

    const uploadButton = document.getElementById("uploadButton");
    const uploadButtonText = document.getElementById("uploadButtonText");
    const uploadSpinner = document.getElementById("uploadSpinner");
    const audioPlayerWrapper = document.getElementById("audioPlayerWrapper");
    const audioPlayer = document.getElementById("audioPlayer");

    // --- UI updates for loading state ---
    uploadButton.disabled = true;
    uploadButtonText.textContent = "Processing...";
    uploadSpinner.classList.remove("hidden");
    audioPlayerWrapper.classList.add("hidden");
    showStatus("Initializing upload...", "info");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("voice", document.getElementById("voices").value);
    formData.append("rate", `${document.getElementById("rate").value < 0 ? "" : "+"}${document.getElementById("rate").value}%`);
    formData.append("volume", `${document.getElementById("volume").value < 0 ? "" : "+"}${document.getElementById("volume").value}%`);
    formData.append("pitch", `${document.getElementById("pitch").value < 0 ? "" : "+"}${document.getElementById("pitch").value}Hz`);

    try {
        showStatus("Uploading PDF...", "info");

        const response = await fetch('/uploadPDF', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: "An unknown error occurred." }));
            throw new Error(errorData.error || "Failed to generate audio.");
        }

        const data = await response.json();
        const audioUrl = data.link;

        if (!audioUrl) {
            throw new Error("Backend did not return an audio link.");
        }

        showStatus("Audio generated successfully! Preparing for download and playback.", "success");

        // Fetch the audio blob to play and download
        const audioResponse = await fetch(audioUrl);
        if (!audioResponse.ok) {
            throw new Error("Failed to fetch the generated audio file.");
        }
        const audioBlob = await audioResponse.blob();
        const blobUrl = URL.createObjectURL(audioBlob);

        // Set up audio player
        audioPlayer.src = blobUrl;
        audioPlayerWrapper.classList.remove("hidden");
        audioPlayer.play();

        // Trigger download
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `${file.name.replace('.pdf', '')}.mp3`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

    } catch (error) {
        console.error('Error:', error);
        showStatus(`Error: ${error.message}`, "error");
    } finally {
        // --- Reset UI from loading state ---
        uploadButton.disabled = false;
        uploadButtonText.textContent = "Generate & Download";
        uploadSpinner.classList.add("hidden");
    }
}

function showStatus(message, type = "info") {
    const statusContainer = document.getElementById("status-container");
    let colorClass = "text-slate-600";
    if (type === "success") colorClass = "text-green-600";
    if (type === "error") colorClass = "text-red-600";

    statusContainer.innerHTML = `<p class="${colorClass} font-medium">${message}</p>`;
}
