let web3;
let contract;
let contractABI;

const contractAddress = "0x2A3aC40C8636eA29e9C4398Beb922d61bf4ABbE3";

const connectWalletBtn = document.getElementById("connect-wallet-btn");
const ccSection = document.getElementById("cc-section");
const submitCcBtn = document.getElementById("submit-cc-btn");
const ccInput = document.getElementById("cc-input");
const ccStatus = document.getElementById("cc-status");

async function loadABI() {
  try {
    const response = await fetch("/contract_abi.json");
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    contractABI = await response.json();
    console.log("✅ ABI loaded.");
  } catch (err) {
    console.error("Failed to load ABI:", err);
    alert("Couldn't load contract ABI.");
  }
}

async function getActiveAccount() {
  const accounts = await window.ethereum.request({ method: "eth_accounts" });
  return accounts[0]; // returns the active account, or undefined
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
    connectWalletBtn.textContent = `Connected: ${activeAccount}`;
    connectWalletBtn.disabled = true;
    ccSection.style.display = "block";
  } catch (err) {
    console.error("Wallet connection failed:", err);
    alert("Connection failed.");
  }
}

async function submitCC() {
  const cc = ccInput.value.trim(); // Always a string
  if (!cc) {
    ccStatus.textContent = "Please enter your CC";
    ccStatus.style.color = "red";
    return;
  }

  try {
    ccStatus.textContent = "Submitting CC...";
    ccStatus.style.color = "black";

    const ccHash = web3.utils.keccak256(cc); // Step 1: Hash it

    // Step 2: Save both CC and its hash to university backend
    await fetch('http://127.0.0.1:5000/api/store-cc', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cc, ccHash })
    });

    // Step 3: Send only hash to blockchain
    const accounts = await web3.eth.getAccounts();
    const from = accounts[0];

    const tx = await contract.methods.submitCC(ccHash).send({
      from,
      gas: 300000
    });

    ccStatus.textContent = "✅ CC submitted!";
    ccStatus.style.color = "green";
    ccInput.value = "";
    console.log("Transaction hash:", tx.transactionHash);

  } catch (err) {
    console.error("Submit failed:", err);

    const message = err.message || "";

    if (message.includes("Already submitted")) {
      ccStatus.textContent = "❌ This CC has already been submitted.";
    } else {
      ccStatus.textContent = "❌ Submission failed: " + message;
    }

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
