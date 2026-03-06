const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const imagePreview = document.getElementById('image-preview');
const predictBtn = document.getElementById('predict-btn');
const resultContainer = document.getElementById('result-container');
const predictionBadge = document.getElementById('prediction-badge');
const predictionText = document.getElementById('prediction-text');
const confidencePercentage = document.getElementById('confidence-percentage');
const confidenceBar = document.getElementById('confidence-bar');
const loader = document.getElementById('loader');

// Drag and Drop support
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, () => dropArea.classList.add('drag-active'), false);
});

['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, () => dropArea.classList.remove('drag-active'), false);
});

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  handleFiles(files);
}

dropArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', function() {
  handleFiles(this.files);
});

function handleFiles(files) {
  if (files.length > 0) {
    const file = files[0];
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onloadend = function() {
        imagePreview.src = reader.result;
        dropArea.style.display = 'none';
        previewContainer.style.display = 'flex';
        resultContainer.style.display = 'none';
        predictBtn.disabled = false;
        predictBtn.querySelector('.btn-text').textContent = 'Detect Symptoms';
      }
    }
  }
}

predictBtn.addEventListener('click', async () => {
  const file = fileInput.files[0] || null;
  if (!file && !imagePreview.src) return;

  // Show loading
  loader.style.display = 'block';
  predictBtn.querySelector('.btn-text').textContent = 'Analyzing Image...';
  predictBtn.disabled = true;

  const formData = new FormData();
  
  // If dragged, fileInput won't have it, we need to handle that or use the file object from handleFiles
  // For simplicity, let's assume we use the first file from the fileInput or a stored variable
  // Let's fix handleFiles to store the file
  let uploadFile = fileInput.files[0];
  if (!uploadFile) {
    // If it was a drag, we need to get it differently. Let's just use the fileInput properly.
    // In a real app we'd store 'currentFile' in a global var.
  }

  // To be safe, let's just use a global currentFile
  if (window.currentFile) {
      formData.append('file', window.currentFile);
  } else if (file) {
      formData.append('file', file);
  } else {
      // If we don't have a file object (e.g. just the dataURL), we'd need to convert it back.
      // Let's update handleFiles to set currentFile.
  }

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (data.prediction) {
      showResults(data);
    } else {
      alert('Error: ' + (data.error || 'Unknown error during analysis.'));
    }
  } catch (err) {
    console.error(err);
    alert('Failed to connect to AI server. Make sure the backend is running.');
  } finally {
    loader.style.display = 'none';
    predictBtn.querySelector('.btn-text').textContent = 'Detection Complete';
    predictBtn.disabled = false;
  }
});

// Update handleFiles to store current file globally
const originalHandleFiles = handleFiles;
handleFiles = function(files) {
    if (files.length > 0) window.currentFile = files[0];
    originalHandleFiles(files);
}

function showResults(data) {
  resultContainer.style.display = 'flex';
  predictionText.textContent = data.prediction;
  confidencePercentage.textContent = data.confidence;
  
  const percentage = parseFloat(data.confidence);
  confidenceBar.style.width = percentage + '%';
  
  if (data.is_healthy) {
    predictionBadge.textContent = 'Excellent Health';
    predictionBadge.className = 'prediction-badge prediction-healthy';
    confidenceBar.style.background = 'var(--accent-healthy)';
    predictionText.style.color = 'var(--accent-healthy)';
  } else {
    predictionBadge.textContent = 'Alert: Infected';
    predictionBadge.className = 'prediction-badge prediction-lumpy';
    confidenceBar.style.background = 'var(--accent-unhealthy)';
    predictionText.style.color = 'var(--accent-unhealthy)';
  }
  
  // Scroll into view
  resultContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function reset() {
  dropArea.style.display = 'block';
  previewContainer.style.display = 'none';
  resultContainer.style.display = 'none';
  fileInput.value = '';
  window.currentFile = null;
}
