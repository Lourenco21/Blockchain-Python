const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileName');
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

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    alert("Por favor, selecione um arquivo PDF primeiro.");
    return;
  }
  if (!isPDF(file)) {
    alert("Arquivo inválido! Selecione um arquivo PDF.");
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:5000/validate-diploma', {
      method: 'POST',
      body: formData
    });
    const result = await response.json();

    if (result.valid) {
      fileNameDisplay.textContent = "Diploma Reconhecido";
      alert("Diploma válido e reconhecido.");
    } else {
      fileNameDisplay.textContent = "Ficheiro não é diploma";
      alert("Ficheiro inválido: " + result.message);
    }
  } catch (error) {
    alert("Erro ao validar o arquivo: " + error.message);
  }
});
