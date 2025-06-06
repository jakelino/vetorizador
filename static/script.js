document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('vetorForm');
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const processBtn = document.getElementById('processBtn');
    const resultSection = document.getElementById('resultSection');

    // Sliders e seus valores
    const sliders = {
        threshold: { slider: document.getElementById('threshold'), value: document.getElementById('thresholdValue') },
        opacity: { slider: document.getElementById('opacity'), value: document.getElementById('opacityValue') },
        grouping: { slider: document.getElementById('grouping'), value: document.getElementById('groupingValue') },
        contrast: { slider: document.getElementById('contrast'), value: document.getElementById('contrastValue') },
        brightness: { slider: document.getElementById('brightness'), value: document.getElementById('brightnessValue') },
        saturation: { slider: document.getElementById('saturation'), value: document.getElementById('saturationValue') },
        smooth: { slider: document.getElementById('smooth'), value: document.getElementById('smoothValue') },
        scale: { slider: document.getElementById('scale'), value: document.getElementById('scaleValue') }
    };

    // Atualizar valores dos sliders
    Object.keys(sliders).forEach(key => {
        const { slider, value } = sliders[key];
        slider.addEventListener('input', function() {
            value.textContent = this.value + (key === 'scale' ? 'x' : '');
        });
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect(files[0]);
        }
    });

    // Seleção de arquivo
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <p><strong>Arquivo:</strong> ${file.name}</p>
                <p><strong>Tamanho:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            `;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    // Envio do formulário
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!fileInput.files[0]) {
            alert('Por favor, selecione uma imagem primeiro!');
            return;
        }

        const formData = new FormData(form);
        
        // Mostrar loading
        processBtn.disabled = true;
        processBtn.querySelector('.btn-text').textContent = 'Processando...';
        processBtn.querySelector('.loading-spinner').style.display = 'block';

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.blob();
            } else {
                return response.json().then(data => {
                    throw new Error(data.error || 'Erro no processamento');
                });
            }
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const filename = getFilename(fileInput.files[0].name, document.getElementById('format').value);
            
            resultSection.innerHTML = `
                <h2>✅ Resultado</h2>
                <div class="result-card">
                    <p>🎉 Vetorização concluída com sucesso!</p>
                    <p><strong>Arquivo:</strong> ${filename}</p>
                    <a href="${url}" download="${filename}" class="download-btn">
                        📥 Download da Imagem Vetorizada
                    </a>
                </div>
            `;
            resultSection.style.display = 'block';
            resultSection.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            alert('Erro: ' + error.message);
        })
        .finally(() => {
            // Esconder loading
            processBtn.disabled = false;
            processBtn.querySelector('.btn-text').textContent = '🚀 Vetorizar Imagem';
            processBtn.querySelector('.loading-spinner').style.display = 'none';
        });
    });

    function getFilename(originalName, format) {
        const baseName = originalName.split('.').slice(0, -1).join('.');
        return `${baseName}_vetorizado.${format}`;
    }
});

