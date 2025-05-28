let web3;
let subscription;
let contract;
let contractABI;

<<<<<<< Updated upstream
const contractAddress = "0x5873779105bCFFE7E7DBF7dAE13075a61E3E6bDB";
=======
const contractAddress = "0xE9633177ae8Ae9310E377F43226a69236124a3A4";
>>>>>>> Stashed changes

const connectWalletBtn = document.getElementById("connect-wallet-btn");
const ccSection = document.getElementById("cc-section");
const submitCcBtn = document.getElementById("submit-cc-btn");
const ccInput = document.getElementById("cc-input");
const ccStatus = document.getElementById("cc-status");
const walletConnected = document.getElementById("wallet-connected");
const paymentSection = document.getElementById("payment-section");
const costLabel = document.getElementById("cost-label");

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

    web3 = new Web3("http://172.24.192.1:7545"); // HTTP provider

    contract = new web3.eth.Contract(contractABI, contractAddress);

    // Instead of .once() with WS, fetch past events periodically or on demand
    // Example to get events from latest block periodically:
    setInterval(async () => {
      try {
        const events = await contract.getPastEvents('StudentMarkedEligible', {
          fromBlock: 'latest',
          toBlock: 'latest'
        });
        events.forEach(event => {
          // check event.returnValues.ccHash and update UI accordingly
        });
      } catch (e) {
        console.error(e);
      }
    }, 5000); // every 5 seconds or adjust interval

    console.log("✅ Connected account:", activeAccount);
    connectWalletBtn.disabled = true;
    ccSection.style.display = "block";
    connectWalletBtn.style.display = 'none';
    walletConnected.style.display = 'inline-block';
    walletConnected.textContent = `Connected wallet: ${activeAccount}`;

    await updateFee();
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

    await checkEvents(ccHash);
    console.log(ccHash);

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

async function checkEvents(ccHash) {
  try {
    const studentMarkedEligible = await contract.getPastEvents('StudentMarkedEligible', {
      fromBlock: 0,
      toBlock: 'latest'
    });

    const studentAlreadyEligible = await contract.getPastEvents('StudentAlreadyEligible', {
      fromBlock: 0,
      toBlock: 'latest'
    });

    const studentMarkedIneligible = await contract.getPastEvents('StudentMarkedIneligible', {
      fromBlock: 0,
      toBlock: 'latest'
    });

    const studentAlreadyIneligible = await contract.getPastEvents('StudentAlreadyIneligible', {
      fromBlock: 0,
      toBlock: 'latest'
    });


    const eligibleEvent = studentMarkedEligible.find(e => e.returnValues.ccHash === ccHash);
    if (eligibleEvent) {
      ccStatus.textContent = "This cc is eligible for the diploma!";
      ccStatus.style.color = "green";
      ccSection.style.display = "none";
      paymentSection.style.display = "block";
      return true;
    }

    const alreadyEligibleEvent = studentAlreadyEligible.find(e => e.returnValues.ccHash === ccHash);
    if (alreadyEligibleEvent) {
      ccStatus.textContent = "This cc is already eligible for the diploma!";
      ccStatus.style.color = "green";
      ccSection.style.display = "none";
      paymentSection.style.display = "block";
      return true;
    }

    const ineligibleEvent = studentMarkedIneligible.find(e => e.returnValues.ccHash === ccHash);
    if (ineligibleEvent) {
      ccStatus.textContent = "This cc is not eligible for the diploma!";
      ccStatus.style.color = "red";
      return false;
    }

    const alreadyIneligibleEvent = studentAlreadyIneligible.find(e => e.returnValues.ccHash === ccHash);
    if (alreadyIneligibleEvent) {
      ccStatus.textContent = "This cc is still not eligible for the diploma!";
      ccStatus.style.color = "red";
      return false;
    }

    return false;
  } catch (err) {
    console.error('Error checking events:', err);
  }
}

async function updateFee() {
  try {
    const feeWei = await contract.methods.getFee().call();
    const feeEth = web3.utils.fromWei(feeWei, "ether");

    // Fetch ETH to EUR exchange rate from a public API (example: CoinGecko)
    const response = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=eur");
    const data = await response.json();
    const ethToEur = data.ethereum.eur;

    const feeEur = (parseFloat(feeEth) * ethToEur).toFixed(2);

    costLabel.textContent = `Cost: ${feeEth} ETH (~${feeEur} €)`;
  } catch (err) {
    console.error("Failed to fetch fee or exchange rate:", err);
    costLabel.textContent = "Cost: (error fetching fee)";
  }
}


connectWalletBtn.onclick = connectWallet;
submitCcBtn.onclick = submitCC;
