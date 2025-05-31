const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileName');
const verificationStatus = document.getElementById('verification-status');
const ccInput = document.getElementById('ccInput')
const uploadForm = document.getElementById('uploadForm');

function isPDF(file) {
  const isMimePDF = file.type === 'application/pdf';
  const isExtPDF = file.name.toLowerCase().endsWith('.pdf');
  return isMimePDF && isExtPDF;
}

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file) {
    if (isPDF(file)) {
      fileNameDisplay.textContent = `Selected: ${file.name}`;
    } else {
      fileNameDisplay.textContent = "Error: only PDF files are allowed";
      fileInput.value = '';
      alert("Select a valid PDF file.");
    }
  } else {
    fileNameDisplay.textContent = "No file selected";
  }
});
ccInput.addEventListener('change', () => {
  const cc = ccInput.value;

});

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  const cc = ccInput.value.trim();
  if (!file) {
    alert("Select a PDF file first.");
    return;
  }
  if (!isPDF(file)) {
    alert("Ivalid file! Select a PDF file.");
    return;
  }
  if (!cc) {
    alert("Insert your CC.");
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('cc', cc);
  verificationStatus.style.display = "inline-block";
  verificationStatus.textContent = `Verifying the combination Diploma: ${file.name} <=> CC: ${cc}...`;
  try {
    const response = await fetch('http://127.0.0.1:5000/api/diploma-validation', {
      method: 'POST',
      body: formData
    });
    const result = await response.json();

    if (response.ok && result.valid) {
      console.log("valid")
      verificationStatus.style.display = "inline-block";
      verificationStatus.textContent = "✅ This diploma is accredited and recognized";
      verificationStatus.style.fontWeight = "bold";
      verificationStatus.style.fontSize = "1.5rem";

    } else {
      console.log("not valid")
      verificationStatus.style.display = "inline-block";
      verificationStatus.textContent = "❌ This diploma is not accredited or recognized";
      verificationStatus.style.fontWeight = "bold";
      verificationStatus.style.fontSize = "1.5rem";
    }

  } catch (error) {
    verificationStatus.style.display = "inline-block";
    verificationStatus.textContent = "⚠️ Error in validation";
    verificationStatus.style.fontWeight = "bold";
    verificationStatus.style.fontSize = "1.5rem";
  }
});
