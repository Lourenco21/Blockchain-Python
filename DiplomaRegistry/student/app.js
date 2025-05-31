let web3;
let contract;
let contractABI;
let lastCcHash = null;
let activeAccount = null;
let activecc = null;

const contractAddress = "0xc1ac64b3730dC4c59af6129943f24341E562432A";

const connectWalletBtn = document.getElementById("connect-wallet-btn");
const ccSection = document.getElementById("cc-section");
const submitCcBtn = document.getElementById("submit-cc-btn");
const ccInput = document.getElementById("cc-input");
const ccStatus = document.getElementById("cc-status");
const walletConnected = document.getElementById("wallet-connected");
const paymentSection = document.getElementById("payment-section");
const costLabel = document.getElementById("cost-label");
const payBtn = document.getElementById("pay-btn");
const paymentStatus = document.getElementById("payment-status");
const downloadPdfBtn = document.getElementById("download-pdf-btn");

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
    activeAccount = accounts[0];

    if (!contractABI) await loadABI();

    web3 = new Web3(window.ethereum); // HTTP provider

    contract = new web3.eth.Contract(contractABI, contractAddress);

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
    const from = activeAccount;
    activecc = cc;
    lastCcHash = ccHash;

    // Submit transaction
    const tx = await contract.methods.submitCC(ccHash).send({ from, gas: 300000 });

    // ✅ Get block number from transaction receipt
    const receipt = await web3.eth.getTransactionReceipt(tx.transactionHash);
    const txBlock = receipt.blockNumber;

    ccStatus.textContent = "✅ CC submitted!";
    ccStatus.style.color = "green";
    ccInput.value = "";

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

    await new Promise(resolve => setTimeout(resolve, 1500));
    await checkEvents(ccHash, txBlock);
    console.log(ccHash);
  } catch (err) {
    console.error("Submit failed:", err);
    ccStatus.textContent = "❌ " + (err.message || "Unknown error");
    ccStatus.style.color = "red";
  }
}


async function payForDiploma() {
  paymentStatus.textContent = "Processing payment...";
  await new Promise(resolve => setTimeout(resolve, 1000));
  if (!lastCcHash) {
    paymentStatus.textContent = "Submit your CC first.";
    paymentStatus.style.color = "red";
    return;
  }
  try {
    paymentStatus.textContent = "Processing payment...";
    paymentStatus.style.color = "black";

    const from = activeAccount;
    const feeWei = await contract.methods.getFee().call();

    // Envia a transação para o contrato
    const tx = await contract.methods.payForDiploma(lastCcHash).send({
      from,
      value: feeWei,
      gas: 300000
    });

    paymentStatus.textContent = "✅ Payment done successfully!";
    paymentStatus.style.color = "green";
    downloadPdfBtn.style.display = "inline-block";
    console.log("Tx hash:", tx.transactionHash);
  } catch (err) {
    console.error("Error on payment:", err);
    paymentStatus.textContent = "❌ " + (err.message || "Unknown error");
    paymentStatus.style.color = "red";
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

async function checkEvents(ccHash, block) {
  try {
    const currentBlock = await web3.eth.getBlockNumber();

    const studentMarkedEligible = await contract.getPastEvents('StudentMarkedEligible', {
      fromBlock: block,
      toBlock: 'latest'
    });

    const studentAlreadyEligible = await contract.getPastEvents('StudentAlreadyEligible', {
      fromBlock: block,
      toBlock: 'latest'
    });

    const studentMarkedIneligible = await contract.getPastEvents('StudentMarkedIneligible', {
      fromBlock: block,
      toBlock: 'latest'
    });



    const eligibleEvent = studentMarkedEligible.find(e => e.returnValues.ccHash === ccHash);
    if (eligibleEvent) {
      ccStatus.textContent = "This cc is eligible for the diploma!";
      ccStatus.style.color = "green";
      ccSection.style.display = "none";
      paymentSection.style.display = "block";
    }

    const alreadyEligibleEvent = studentAlreadyEligible.find(e => e.returnValues.ccHash === ccHash);
    if (alreadyEligibleEvent) {
      ccStatus.textContent = "This cc is already eligible for the diploma!";
      ccStatus.style.color = "green";
      ccSection.style.display = "none";
      paymentSection.style.display = "block";
    }

    const ineligibleEvent = studentMarkedIneligible.find(e => e.returnValues.ccHash === ccHash);
    if (ineligibleEvent) {
      const reason = ineligibleEvent.returnValues.reason;
      ccStatus.textContent = `${reason}`;
      ccStatus.style.color = "red";
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

downloadPdfBtn.addEventListener("click", async () => {
  // Get the CC from the input or prompt the user if not available
  const cc = activecc;
  if (!cc) return alert("CC not provided.");

  // Request the student number from the backend using the CC
  const resp = await fetch(`http://127.0.0.1:5000/api/student-id?cc=${cc}`);
  if (!resp.ok) return alert("Error fetching student number.");
  const { student_id } = await resp.json();

  // Download the PDF using the student number
  const response = await fetch(`http://127.0.0.1:5000/api/diploma-pdf?student_id=${student_id}`);
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `diploma_${student_id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } else {
    alert("Error downloading diploma.");
  }
});


connectWalletBtn.onclick = connectWallet;
submitCcBtn.onclick = submitCC;
payBtn.onclick = payForDiploma;
