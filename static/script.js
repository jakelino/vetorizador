document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('vetorForm');
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const processBtn = document.getElementById('processBtn');
    const resultSection = document.getElementById('resultSection');
    const processInfo = document.getElementById('processInfo');

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
                } else if (key === 'quality') {
                    displayValue += '%';
                    updateQualityFeedback(this.value);
                    document.getElementById('currentQuality').textContent = this.value;
                } else if (key === 'contrast' || key === 'brightness' || key === 'saturation') {
                    displayValue = parseFloat(this.value).toFixed(1);
                }
                value.textContent = displayValue;
            });
        }
    });

    function updateQualityFeedback(qualityValue) {
        const qualityDescription = document.getElementById('qualityDescription');
        const quality = parseInt(qualityValue);
        
        let description = '';
        if (quality <= 20) {
            description = '🔴 Qualidade Muito Baixa - Arquivo muito pequeno, baixa definição';
        } else if (quality <= 40) {
            description = '🟠 Qualidade Baixa - Arquivo pequeno, definição reduzida';
        } else if (quality <= 60) {
            description = '🟡 Qualidade Média - Balance entre tamanho e definição';
        } else if (quality <= 80) {
            description = '🟢 Qualidade Alta - Arquivo maior, boa definição';
        } else {
            description = '🔵 Qualidade Máxima - Arquivo grande, excelente definição';
        }
        
        qualityDescription.textContent = description;
    }

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
            alert('❌ Tipo de arquivo não suportado! Use PNG, JPG, BMP, GIF, TIFF ou WebP.');
            return;
        }

        // Validar tamanho (16MB)
        if (file.size > 16 * 1024 * 1024) {
            alert('❌ Arquivo muito grande! Máximo permitido: 16MB.');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                imagePreview.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <div style="margin-top: 15px; text-align: left;">
                        <p><strong>📄 Arquivo:</strong> ${file.name}</p>
                        <p><strong>📏 Dimensões:</strong> ${img.width} × ${img.height} pixels</p>
                        <p><strong>💾 Tamanho Original:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
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
            alert('❌ Por favor, selecione uma imagem primeiro!');
            return;
        }

        const formData = new FormData(form);
        const qualityValue = document.getElementById('quality').value;
        
        // GARANTIR QUE A QUALIDADE SEJA ENVIADA
        formData.set('quality', qualityValue);
        
        // Debug detalhado
        console.log('=== DADOS SENDO ENVIADOS ===');
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }
        
        // Mostrar loading
        processBtn.disabled = true;
        processBtn.querySelector('.btn-text').textContent = 'PROCESSANDO...';
        processBtn.querySelector('.loading-spinner').style.display = 'block';
        processInfo.style.display = 'block';
        processInfo.innerHTML = `Processando com qualidade <strong>${qualityValue}%</strong>...`;

        // Esconder resultado anterior
        resultSection.style.display = 'none';

        const startTime = Date.now();

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
            const endTime = Date.now();
            const processingTime = ((endTime - startTime) / 1000).toFixed(1);
            
            const url = URL.createObjectURL(blob);
            const filename = getFilename(fileInput.files[0].name, document.getElementById('format').value, qualityValue);
            const fileSize = (blob.size / 1024 / 1024).toFixed(2);
            const originalSize = (fileInput.files[0].size / 1024 / 1024).toFixed(2);
            const compressionRatio = ((1 - blob.size / fileInput.files[0].size) * 100).toFixed(1);
            
            resultSection.innerHTML = `
                <h2>✅ Vetorização Concluída com Sucesso!</h2>
                <div class="result-card">
                    <div style="font-size: 4em; margin-bottom: 20px;">🎉</div>
                    <h3 style="color: #4CAF50; margin-bottom: 20px;">Arquivo processado com qualidade ${qualityValue}%</h3>
                    
                    <div style="margin: 25px 0; text-align: left; background: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <h4 style="margin-bottom: 15px; color: #333;">📊 Estatísticas do Processamento:</h4>
                        <p><strong>📄 Arquivo Final:</strong> ${filename}</p>
                        <p><strong>💾 Tamanho Original:</strong> ${originalSize} MB</p>
                        <p><strong>💾 Tamanho Final:</strong> ${fileSize} MB</p>
                        <p><strong>📊 Taxa de Compressão:</strong> ${compressionRatio > 0 ? compressionRatio : 0}%</p>
                        <p><strong>🎯 Qualidade Aplicada:</strong> ${qualityValue}%</p>
                        <p><strong>⏱️ Tempo de Processamento:</strong> ${processingTime}s</p>
                        <p><strong>🕒 Concluído em:</strong> ${new Date().toLocaleTimeString()}</p>
                    </div>
                    
                    <a href="${url}" download="${filename}" class="download-btn">
                        📥 DOWNLOAD DA IMAGEM VETORIZADA
                    </a>
                </div>
            `;
            resultSection.style.display = 'block';
            resultSection.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            alert('❌ Erro no processamento: ' + error.message);
            console.error('Erro detalhado:', error);
        })
        .finally(() => {
            // Esconder loading
            processBtn.disabled = false;
            processBtn.querySelector('.btn-text').textContent = '🚀 VETORIZAR IMAGEM';
            processBtn.querySelector('.loading-spinner').style.display = 'none';
            processInfo.style.display = 'none';
        });
    });

    function getFilename(originalName, format, quality) {
        const baseName = originalName.split('.').slice(0, -1).join('.');
        return `${baseName}_vetorizado_q${quality}.${format}`;
    }

    // Inicializar feedback da qualidade
    updateQualityFeedback(50);
});
