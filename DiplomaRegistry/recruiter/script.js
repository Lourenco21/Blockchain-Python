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
      fileNameDisplay.textContent = `Selecionado: ${file.name}`;
    } else {
      fileNameDisplay.textContent = "Erro: Só são permitidos arquivos PDF";
      fileInput.value = '';
      alert("Por favor, selecione um arquivo PDF válido.");
    }
  } else {
    fileNameDisplay.textContent = "Nenhum arquivo selecionado";
  }
});
ccInput.addEventListener('change', () => {
  const cc = ccInput.value;

});

uploadForm.addEventListener('submit', async (e) => {
  console.log("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
  e.preventDefault();
  const file = fileInput.files[0];
  const cc = ccInput.value.trim();
  if (!file) {
    alert("Por favor, selecione um arquivo PDF primeiro.");
    return;
  }
  if (!isPDF(file)) {
    alert("Arquivo inválido! Selecione um arquivo PDF.");
    return;
  }
  if (!cc) {
    alert("Por favor, insira o número do CC.");
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('cc', cc);
  console.log("BBBBBBBBBBBBBB")
  verificationStatus.style.display = "inline-block";
  verificationStatus.textContent = "A verificar a combinação Diploma <=> CC";
  try {
    const response = await fetch('http://127.0.0.1:5000/api/diploma-validation', {
      method: 'POST',
      body: formData
    });
    const result = await response.json();

    if (response.ok && result.valid) {
      console.log("valid")
      verificationStatus.style.display = "inline-block";
      verificationStatus.textContent = "✅ Diploma reconhecido";

    } else {
      console.log("not valid")
      verificationStatus.style.display = "inline-block";
      verificationStatus.textContent = "❌ Diploma inválido";
    }

  } catch (error) {
    verificationStatus.style.display = "inline-block";
    verificationStatus.textContent = "⚠️ Erro na validação";
  }
});
