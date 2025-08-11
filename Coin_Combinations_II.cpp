
#include <bits/stdc++.h>
#define ll long long
using namespace std;
const int mod = 1e9 + 7;

void solve() {
    int n, x; cin>>n>>x;
    vector<int> c(n); for(int & i: c) cin>>i;

    vector<vector<int>> dp(n, vector<int>(x+1, 0));
    dp[0][0] = 1;
    for(int i = 0;i<n;i++){
        int sum = 0;
        for(int j = 0; j<=x;j++){
            if(j - c[i] >= 0){
                sum = dp[i][j - c[i]] + dp[i-1][j-c[i]];
            }
            dp[i][j] = sum;
        }
    }

    cout<<dp[n-1][x]<<endl;


}   

int main() {
    int t; cin>>t; 
    while(t--)
        solve();
    return 0;
}