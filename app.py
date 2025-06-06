from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageFilter, ImageEnhance
import io
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
    file = request.files['file']
    
    if not (file and allowed_file(file.filename)):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

    try:
        # RECEBER TODOS OS PARÂMETROS
        quality = int(request.form.get('quality', 50))
        threshold = int(request.form.get('threshold', 128))
        opacity = int(request.form.get('opacity', 10))
        grouping = int(request.form.get('grouping', 1))
        contrast = float(request.form.get('contrast', 1.0))
        brightness = float(request.form.get('brightness', 1.0))
        scale = int(request.form.get('scale', 1))
        bg_color = request.form.get('bg_color', '#ffffff')
        output_format = request.form.get('format', 'jpg').lower()

        print(f"QUALIDADE RECEBIDA: {quality}")
        print(f"FORMATO: {output_format}")

        # PROCESSAR IMAGEM
        img = Image.open(file.stream).convert('RGBA')
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
            
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
        
        if scale > 1:
            new_width = img.width * scale
            new_height = img.height * scale
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # APLICAR QUALIDADE POR FORMATO
        output = io.BytesIO()
        
        if output_format in ['jpg', 'jpeg']:
            # JPEG: Remover transparência e aplicar qualidade
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            img.save(output, format='JPEG', quality=quality, optimize=True)
            mimetype = 'image/jpeg'
            ext = 'jpg'
            
        elif output_format == 'png':
            # PNG: Usar compress_level baseado na qualidade
            compress_level = max(0, min(9, int((100 - quality) / 11)))
            
            if quality < 50:
                # Reduzir cores para qualidade baixa
                img = img.quantize(colors=max(16, quality * 2))
            
            img.save(output, format='PNG', compress_level=compress_level, optimize=True)
            mimetype = 'image/png'
            ext = 'png'
            
        elif output_format == 'webp':
            img.save(output, format='WEBP', quality=quality, method=6)
            mimetype = 'image/webp'
            ext = 'webp'
            
        else:
            img.save(output, format=output_format.upper())
            mimetype = f'image/{output_format}'
            ext = output_format

        output.seek(0)
        final_size = len(output.getvalue())
        
        filename_base = os.path.splitext(file.filename)[0]
        output_filename = f'{filename_base}_q{quality}.{ext}'
        
        print(f"ARQUIVO FINAL: {output_filename} - {final_size/1024/1024:.2f} MB")
        
        return send_file(
            output,
            mimetype=mimetype,
            download_name=output_filename,
            as_attachment=True
        )
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({'error': f'Erro: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
