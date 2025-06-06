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
        quality = int(request.form.get('quality', 80))  # CORREÇÃO AQUI
        bg_color = request.form.get('bg_color', '#ffffff')
        output_format = request.form.get('format', 'svg').lower()
        vectorize_mode = request.form.get('vectorize_mode', 'color')

        print(f"QUALIDADE RECEBIDA: {quality}")  # Debug

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

        # Gerar saída baseada no formato
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
        else:
            # Para outros formatos, aplicar processamento
            if vectorize_mode == 'bw':
                img = img.convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
            
            # CORREÇÃO PRINCIPAL: Aplicar qualidade corretamente baseada no formato
            if output_format in ['jpg', 'jpeg']:
                # JPG não suporta transparência
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Criar fundo branco para transparência
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                img.save(output, format='JPEG', quality=quality, optimize=True)
                print(f"JPG salvo com qualidade: {quality}")  # Debug
                
            elif output_format == 'png':
                # PNG usa compress_level (0-9), convertemos de quality (1-100)
                # quality 1-100 -> compress_level 9-0 (invertido)
                compress_level = max(0, min(9, int((100 - quality) / 11)))
                img.save(output, format='PNG', compress_level=compress_level, optimize=True)
                print(f"PNG salvo com compress_level: {compress_level} (quality: {quality})")  # Debug
                
            elif output_format == 'webp':
                img.save(output, format='WEBP', quality=quality, method=6, lossless=(quality >= 95))
                print(f"WebP salvo com qualidade: {quality}")  # Debug
                
            elif output_format == 'bmp':
                # BMP não tem compressão, converter para RGB se necessário
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                img.save(output, format='BMP')
                print(f"BMP salvo (sem compressão)")  # Debug
                
            elif output_format == 'tiff':
                # TIFF com compressão baseada na qualidade
                compression = 'jpeg' if quality < 95 else 'lzw'
                if compression == 'jpeg' and img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                img.save(output, format='TIFF', compression=compression, quality=quality if compression == 'jpeg' else None)
                print(f"TIFF salvo com compressão: {compression}, qualidade: {quality}")  # Debug
                
            else:
                # Formato genérico
                img.save(output, format=output_format.upper())
                
            mimetype = f'image/{output_format}'
            ext = output_format

        output.seek(0)
        
        # Nome do arquivo de saída
        filename_base = os.path.splitext(file.filename)[0]
        output_filename = f'{filename_base}_vetorizado.{ext}'
        
        print(f"Arquivo final: {output_filename}, tamanho: {len(output.getvalue())} bytes")  # Debug
        
        return send_file(
            output,
            mimetype=mimetype,
            download_name=output_filename,
            as_attachment=True
        )
        
    except Exception as e:
        print(f"ERRO: {str(e)}")  # Debug
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

def image_to_svg_advanced(img, params):
    width, height = img.size
    pixels = img.load()
    
    svg_elements = []
    
    # Adicionar fundo
    svg_elements.append(f'<rect width="{width}" height="{height}" fill="{params["bg_color"]}"/>')
    
    if params['mode'] == 'color':
        # Vetorização colorida
        for y in range(height):
            x = 0
            while x < width:
                r, g, b, a = pixels[x, y]
                
                # Filtrar por opacidade mínima
                if a < (params['opacity_min'] * 255 / 100):
                    x += 1
                    continue
                
                # Agrupamento horizontal
                start_x = x
                current_color = (r, g, b, a)
                group_count = 0
                
                while (x < width and 
                       pixels[x, y] == current_color and 
                       group_count < params['grouping']):
                    x += 1
                    group_count += 1
                
                # Adicionar retângulo colorido
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                opacity = a / 255.0
                rect_width = x - start_x
                
                svg_elements.append(
                    f'<rect x="{start_x}" y="{y}" width="{rect_width}" height="1" '
                    f'fill="{hex_color}" fill-opacity="{opacity:.3f}"/>'
                )
    
    else:  # modo preto e branco
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
    
    # Construir SVG completo
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
