let web3;
let contract;
let contractABI;

const contractAddress = "0xBdcb5aC5De6218B007b8af9Aef67f92F44b27539";

const connectWalletBtn = document.getElementById("connect-wallet-btn");
const ccSection = document.getElementById("cc-section");
const submitCcBtn = document.getElementById("submit-cc-btn");
const ccInput = document.getElementById("cc-input");
const ccStatus = document.getElementById("cc-status");
const walletConnected = document.getElementById("wallet-connected");

async function loadABI() {
  try {
    const response = await fetch("../contract_abi.json");
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    contractABI = await response.json();
    console.log("✅ ABI loaded.");
  } catch (err) {
    console.error("Failed to load ABI:", err);
    alert("Couldn't load contract ABI.");
  }
}

async function connectWallet() {
  if (typeof window.ethereum === "undefined") {
    alert("MetaMask not detected.");
    return;
  }

  try {
    // Trigger MetaMask prompt to always ask the active account
    const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
    const activeAccount = accounts[0];

    if (!contractABI) await loadABI();

    web3 = new Web3(window.ethereum);
    contract = new web3.eth.Contract(contractABI, contractAddress);

    console.log("✅ Connected account:", activeAccount);
    connectWalletBtn.disabled = true;
    ccSection.style.display = "block";
    connectWalletBtn.style.display = 'none';
    walletConnected.style.display = 'inline-block';
    walletConnected.textContent = `Connected wallet: ${activeAccount}`;
  } catch (err) {
    console.error("Wallet connection failed:", err);
    alert("Connection failed.");
  }
}

async function submitCC() {
  const cc = ccInput.value.trim();
  if (!cc) {
    ccStatus.textContent = "Please enter your CC";
    ccStatus.style.color = "red";
    return;
  }

  try {
    ccStatus.textContent = "Submitting CC...";
    ccStatus.style.color = "black";

    const ccHash = web3.utils.keccak256(cc);
    const accounts = await web3.eth.getAccounts();
    const from = accounts[0];

    // Send tx to smart contract
    const tx = await contract.methods.submitCC(ccHash).send({ from, gas: 300000 });

    ccStatus.textContent = "✅ CC submitted!";
    ccStatus.style.color = "green";
    ccInput.value = "";

    console.log("Transaction hash:", tx.transactionHash);

    // Now send to Flask backend
    const response = await fetch('http://127.0.0.1:5000/api/store-cc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cc, ccHash })
    });

    const result = await response.json();
    if (response.ok) {
      console.log('Stored in backend:', result.status);
    } else {
      console.error('Backend error:', result.error);
    }
  } catch (err) {
    console.error("Submit failed:", err);
    ccStatus.textContent = "❌ " + (err.message || "Unknown error");
    ccStatus.style.color = "red";
  }
}


if (window.ethereum) {
  // Listen for account change while the DApp is open
  window.ethereum.on("accountsChanged", (accounts) => {
    if (accounts.length === 0) {
      location.reload(); // Reset UI on disconnect
    } else {
      connectWallet(); // Re-run connect logic with new account
    }
  });
}

connectWalletBtn.onclick = connectWallet;
submitCcBtn.onclick = submitCC;
