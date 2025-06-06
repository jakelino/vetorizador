from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageFilter, ImageEnhance
import io
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

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
        # Parâmetros dos controles
        threshold = int(request.form.get('threshold', 128))
        opacity_min = int(request.form.get('opacity', 10))
        grouping = int(request.form.get('grouping', 1))
        smooth = int(request.form.get('smooth', 0))
        scale = int(request.form.get('scale', 1))
        contrast = float(request.form.get('contrast', 1.0))
        brightness = float(request.form.get('brightness', 1.0))
        saturation = float(request.form.get('saturation', 1.0))
        quality = int(request.form.get('quality', 80))
        bg_color = request.form.get('bg_color', '#ffffff')
        output_format = request.form.get('format', 'png').lower()
        vectorize_mode = request.form.get('vectorize_mode', 'color')

        print(f"=== PARÂMETROS RECEBIDOS ===")
        print(f"Qualidade: {quality}")
        print(f"Formato: {output_format}")

        # Processar imagem
        img = Image.open(file.stream).convert('RGBA')
        
        # Aplicar melhorias de imagem
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
            
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
            
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation)
        
        # Aplicar suavização
        if smooth > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=smooth/3))
        
        # Aplicar escala
        if scale > 1:
            new_width = img.width * scale
            new_height = img.height * scale
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # Aplicar vetorização se necessário
        if vectorize_mode == 'bw':
            img = img.convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')

        # CORREÇÃO PRINCIPAL: Aplicar qualidade corretamente por formato
        output = io.BytesIO()
        
        if output_format == 'svg':
            svg_content = image_to_svg_advanced(img, {
                'threshold': threshold,
                'opacity_min': opacity_min,
                'grouping': grouping,
                'bg_color': bg_color,
                'mode': vectorize_mode
            })
            output.write(svg_content.encode('utf-8'))
            mimetype = 'image/svg+xml'
            ext = 'svg'
            
        elif output_format == 'png':
            # PNG: Usar compress_level em vez de quality
            compress_level = convert_quality_to_compress_level(quality)
            
            # Para qualidade muito baixa, reduzir cores drasticamente
            if quality <= 30:
                img = img.quantize(colors=max(8, quality // 2))
            elif quality <= 50:
                img = img.quantize(colors=max(32, quality))
            elif quality <= 70:
                img = img.quantize(colors=min(256, quality * 2))
            
            img.save(output, format='PNG', compress_level=compress_level, optimize=True)
            print(f"PNG salvo com compress_level: {compress_level} (qualidade: {quality})")
            mimetype = 'image/png'
            ext = 'png'
            
        elif output_format in ['jpg', 'jpeg']:
            # JPEG: Converter para RGB e usar quality diretamente
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                img = background
            
            # Garantir que quality está entre 1-95 para JPEG
            jpeg_quality = max(1, min(95, quality))
            img.save(output, format='JPEG', quality=jpeg_quality, optimize=True)
            print(f"JPEG salvo com qualidade: {jpeg_quality}")
            mimetype = 'image/jpeg'
            ext = 'jpg'
            
        elif output_format == 'webp':
            # WebP: Usar quality diretamente
            webp_quality = max(1, min(100, quality))
            lossless = quality >= 95
            img.save(output, format='WEBP', quality=webp_quality, method=6, lossless=lossless)
            print(f"WebP salvo com qualidade: {webp_quality}, lossless: {lossless}")
            mimetype = 'image/webp'
            ext = 'webp'
            
        elif output_format == 'bmp':
            # BMP: Simular qualidade reduzindo cores
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            if quality < 70:
                colors = max(8, quality // 2)
                img = img.quantize(colors=colors)
            
            img.save(output, format='BMP')
            print(f"BMP salvo com {img.mode} (qualidade simulada: {quality})")
            mimetype = 'image/bmp'
            ext = 'bmp'
            
        else:
            # Outros formatos
            img.save(output, format=output_format.upper())
            mimetype = f'image/{output_format}'
            ext = output_format

        output.seek(0)
        final_size = len(output.getvalue())
        
        # Nome do arquivo de saída
        filename_base = os.path.splitext(file.filename)[0]
        output_filename = f'{filename_base}_q{quality}.{ext}'
        
        print(f"=== RESULTADO ===")
        print(f"Arquivo: {output_filename}")
        print(f"Tamanho: {final_size} bytes ({final_size/1024/1024:.2f} MB)")
        
        return send_file(
            output,
            mimetype=mimetype,
            download_name=output_filename,
            as_attachment=True
        )
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

def convert_quality_to_compress_level(quality):
    """Converte qualidade (1-100) para compress_level PNG (0-9)"""
    if quality <= 10:
        return 9  # Máxima compressão
    elif quality <= 20:
        return 8
    elif quality <= 30:
        return 7
    elif quality <= 40:
        return 6
    elif quality <= 50:
        return 5
    elif quality <= 60:
        return 4
    elif quality <= 70:
        return 3
    elif quality <= 80:
        return 2
    elif quality <= 90:
        return 1
    else:
        return 0  # Mínima compressão

def image_to_svg_advanced(img, params):
    width, height = img.size
    pixels = img.load()
    
    svg_elements = []
    svg_elements.append(f'<rect width="{width}" height="{height}" fill="{params["bg_color"]}"/>')
    
    if params['mode'] == 'color':
        for y in range(height):
            x = 0
            while x < width:
                r, g, b, a = pixels[x, y]
                
                if a < (params['opacity_min'] * 255 / 100):
                    x += 1
                    continue
                
                start_x = x
                current_color = (r, g, b, a)
                group_count = 0
                
                while (x < width and 
                       pixels[x, y] == current_color and 
                       group_count < params['grouping']):
                    x += 1
                    group_count += 1
                
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                opacity = a / 255.0
                rect_width = x - start_x
                
                svg_elements.append(
                    f'<rect x="{start_x}" y="{y}" width="{rect_width}" height="1" '
                    f'fill="{hex_color}" fill-opacity="{opacity:.3f}"/>'
                )
    else:
        img_bw = img.convert('L')
        pixels_bw = img_bw.load()
        
        for y in range(height):
            x = 0
            while x < width:
                pixel_value = pixels_bw[x, y]
                
                if pixel_value <= params['threshold']:
                    start_x = x
                    while x < width and pixels_bw[x, y] <= params['threshold']:
                        x += 1
                    
                    rect_width = x - start_x
                    svg_elements.append(
                        f'<rect x="{start_x}" y="{y}" width="{rect_width}" height="1" fill="#000000"/>'
                    )
                else:
                    x += 1
    
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'shape-rendering="crispEdges">\n' +
        '\n'.join(svg_elements) +
        '\n</svg>'
    )
    
    return svg_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
