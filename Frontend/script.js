function updatePitch(){
    let value = document.querySelector("#pitch").value;
    document.querySelector("#pitchDisplay").innerHTML = value;   
}

function updateRate(){
    let value = document.querySelector("#rate").value;
    document.querySelector("#rateDisplay").innerHTML = value;
}

function updateVolume(){
    let value = document.querySelector("#volume").value;
    document.querySelector("#volumeDisplay").innerHTML = value;
}




let linkToDownload = null;


function onFileChange(){
    
    const fileInput = document.querySelector("#pdfFile");
    const file = fileInput.files[0];
    if (file && file.type === "application/pdf") {
        const pdfIframe = document.querySelector("#pdfIframe");
        pdfIframe.src = URL.createObjectURL(file);
        pdfIframe.hidden = false;
    }
}

function uploadPDF(){
    const fileInput = document.querySelector("#pdfFile");
    const file = fileInput.files[0];

    if(!file){
        alert("Please select a PDF file.");
        return;
    }

    let x = document.querySelector("#voices").value;
    const voice = `${x}`;

    x = document.querySelector("#rate").value;
    const rate = `${x<0?"-":"+"}${x}%`;

    x = document.querySelector("#volume").value;
    const volume = `${x<0?"-":"+"}${x}%`;

    x = document.querySelector("#pitch").value;
    const pitch = `${x<0?"-":"+"}${x}Hz`;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("voice", voice);
    formData.append("rate", rate);
    formData.append("volume", volume);
    formData.append("pitch", pitch);

    console.log(file)
    console.log(formData);

    fetch('http://127.0.0.1:8000/uploadPDF', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert("File uploaded successfully!");
        console.log(data);
        linkToDownload = data.link;
        console.log(data);
        updateDownloadButton();
    })
    .catch(error => {
        console.error('Error uploading file:', error);
        alert("Error uploading file: open console for more info");
    });
}

function updateDownloadButton(){
    let button = document.querySelector("#downloadButton");
    if(linkToDownload){
        button.disabled = false;
    } else {
        button.disabled = true;
    }
}


async function downloadAudioFile(){
    if(!linkToDownload){
        alert("Please upload a PDF file first.");
        return;
    }

    const response = await fetch(linkToDownload);
    if(response.ok){
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'audio.mp3';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        
        
        //put in i frame
        const audioIframe = document.querySelector("#audioIframe");
        audioIframe.src = url;
        audioIframe.hidden = false;
        URL.revokeObjectURL(url);
    } else {
        alert("Failed to download audio file.");
    }       
}



/**
 * Toggles the visibility of the voice test area and swaps the expand/collapse icons.
 */
function toggleTestArea() {
    const content = document.querySelector("#voiceTestContent");
    const iconCollapsed = document.querySelector("#icon-collapsed");
    const iconExpanded = document.querySelector("#icon-expanded");

    content.classList.toggle("hidden");
    iconCollapsed.classList.toggle("hidden");
    iconExpanded.classList.toggle("hidden");
}


/**
 * Sends a sample text to the backend to generate a short test audio clip.
 * NOTE: This requires a new backend endpoint, e.g., /test-voice
 */
async function testVoice() {
    const testButton = document.querySelector("#testVoiceButton");
    const testIframe = document.querySelector("#testAudioIframe");

    // Disable button to prevent multiple clicks
    testButton.disabled = true;
    testIframe.classList.add("hidden"); // Hide previous result

    try {
        // Gather current voice settings
        const voice = document.querySelector("#voices").value;
        const rateValue = document.querySelector("#rate").value;
        const volumeValue = document.querySelector("#volume").value;
        const pitchValue = document.querySelector("#pitch").value;

        const rate = `${rateValue >= 0 ? '+' : ''}${rateValue}%`;
        const volume = `${volumeValue >= 0 ? '+' : ''}${volumeValue}%`;
        const pitch = `${pitchValue >= 0 ? '+' : ''}${pitchValue}Hz`;
        
        // --- IMPORTANT ---
        // You need to create a new, simple endpoint on your backend for this.
        // It should accept JSON with 'text' and voice parameters.
        const response = await fetch('http://127.0.0.1:8000/test-voice', { // Assumed new endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: "Hello, this is a test of the selected voice.",
                voice: voice,
                rate: rate,
                volume: volume,
                pitch: pitch,
            }),
        });

        if (!response.ok) {
            throw new Error("Failed to generate test audio.");
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        // Display and play the test audio
        testIframe.src = audioUrl;
        testIframe.classList.remove("hidden");

    } catch (error) {
        console.error("Error testing voice:", error);
        alert("Could not generate test audio. Make sure the backend is running and the /test-voice endpoint is configured.");
    } finally {
        // Re-enable the button
        testButton.disabled = false;
    }
}