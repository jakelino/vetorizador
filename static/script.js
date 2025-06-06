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
        scale: { slider: document.getElementById('scale'), value: document.getElementById('scaleValue') },
        quality: { slider: document.getElementById('quality'), value: document.getElementById('qualityValue') }
    };

    // Atualizar valores dos sliders em tempo real
    Object.keys(sliders).forEach(key => {
        const { slider, value } = sliders[key];
        if (slider && value) {
            slider.addEventListener('input', function() {
                let displayValue = this.value;
                if (key === 'scale') {
                    displayValue += 'x';
                } else if (key === 'contrast' || key === 'brightness' || key === 'saturation') {
                    displayValue = parseFloat(this.value).toFixed(1);
                }
                value.textContent = displayValue;
            });
        }
    });

    // Drag and drop functionality
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
        // Validar tipo de arquivo
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/gif', 'image/tiff', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            alert('Tipo de arquivo não suportado! Use PNG, JPG, BMP, GIF, TIFF ou WebP.');
            return;
        }

        // Validar tamanho (16MB)
        if (file.size > 16 * 1024 * 1024) {
            alert('Arquivo muito grande! Máximo permitido: 16MB.');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                imagePreview.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <div style="margin-top: 10px; text-align: left;">
                        <p><strong>📄 Arquivo:</strong> ${file.name}</p>
                        <p><strong>📏 Dimensões:</strong> ${img.width} × ${img.height} pixels</p>
                        <p><strong>💾 Tamanho:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        <p><strong>🎨 Tipo:</strong> ${file.type}</p>
                    </div>
                `;
                imagePreview.style.display = 'block';
            };
            img.src = e.target.result;
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

        // Esconder resultado anterior
        resultSection.style.display = 'none';

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
            const fileSize = (blob.size / 1024 / 1024).toFixed(2);
            
            resultSection.innerHTML = `
                <h2>✅ Resultado</h2>
                <div class="result-card">
                    <div style="font-size: 3em; margin-bottom: 15px;">🎉</div>
                    <h3>Vetorização concluída com sucesso!</h3>
                    <div style="margin: 20px 0; text-align: left;">
                        <p><strong>📄 Arquivo:</strong> ${filename}</p>
                        <p><strong>💾 Tamanho:</strong> ${fileSize} MB</p>
                        <p><strong>🕒 Processado em:</strong> ${new Date().toLocaleTimeString()}</p>
                    </div>
                    <a href="${url}" download="${filename}" class="download-btn">
                        📥 Download da Imagem Vetorizada
                    </a>
                </div>
            `;
            resultSection.style.display = 'block';
            resultSection.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            alert('❌ Erro: ' + error.message);
            console.error('Erro no processamento:', error);
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

    // Animações suaves
    function animateValue(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Adicionar efeitos visuais aos sliders
    Object.keys(sliders).forEach(key => {
        const { slider } = sliders[key];
        if (slider) {
            slider.addEventListener('mousedown', function() {
                this.style.transform = 'scale(1.02)';
            });
            
            slider.addEventListener('mouseup', function() {
                this.style.transform = 'scale(1)';
            });
        }
    });
});
