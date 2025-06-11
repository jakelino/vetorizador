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
        # CORREÇÃO: Garantir que todos os parâmetros sejam lidos corretamente
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
        print(f"Arquivo original: {file.filename}")

        # Processar imagem
        img = Image.open(file.stream).convert('RGBA')
        original_size = img.size
        print(f"Tamanho original: {original_size}")
        
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
            print(f"Imagem redimensionada para: {img.size}")

        # CORREÇÃO PRINCIPAL: Aplicar qualidade corretamente
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
            # Para formatos raster, aplicar processamento de vetorização se necessário
            if vectorize_mode == 'bw':
                img = img.convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
            
            # APLICAR QUALIDADE CORRETAMENTE BASEADA NO FORMATO
            if output_format in ['jpg', 'jpeg']:
                # JPG: Converter para RGB e aplicar qualidade diretamente
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Aplicar qualidade JPG (1-100)
                img.save(output, format='JPEG', quality=quality, optimize=True)
                print(f"JPG salvo com qualidade: {quality}")
                
            elif output_format == 'png':
                # PNG: Aplicar compressão baseada na qualidade
                # Qualidade 1-100 -> compress_level 9-0 (invertido)
                if quality <= 10:
                    compress_level = 9
                elif quality <= 20:
                    compress_level = 8
                elif quality <= 30:
                    compress_level = 7
                elif quality <= 40:
                    compress_level = 6
                elif quality <= 50:
                    compress_level = 5
                elif quality <= 60:
                    compress_level = 4
                elif quality <= 70:
                    compress_level = 3
                elif quality <= 80:
                    compress_level = 2
                elif quality <= 90:
                    compress_level = 1
                else:
                    compress_level = 0
                
                # CORREÇÃO ADICIONAL: Para qualidade muito baixa, reduzir cores
                if quality < 50:
                    # Reduzir número de cores para diminuir tamanho
                    img = img.quantize(colors=min(256, max(16, quality * 3)))
                
                img.save(output, format='PNG', compress_level=compress_level, optimize=True)
                print(f"PNG salvo com compress_level: {compress_level} (qualidade: {quality})")
                
            elif output_format == 'webp':
                # WebP: Aplicar qualidade diretamente
                lossless = quality >= 95
                img.save(output, format='WEBP', quality=quality, method=6, lossless=lossless)
                print(f"WebP salvo com qualidade: {quality}, lossless: {lossless}")
                
            elif output_format == 'bmp':
                # BMP: Não tem compressão, mas podemos reduzir cores para qualidade baixa
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                if quality < 70:
                    # Reduzir cores para qualidade baixa
                    img = img.quantize(colors=max(16, quality * 2))
                
                img.save(output, format='BMP')
                print(f"BMP salvo (qualidade simulada: {quality})")
                
            elif output_format == 'tiff':
                # TIFF: Usar diferentes tipos de compressão baseados na qualidade
                if quality < 30:
                    compression = 'group4'  # Maior compressão
                elif quality < 60:
                    compression = 'lzw'     # Compressão média
                elif quality < 90:
                    compression = 'jpeg'    # Compressão com qualidade
                else:
                    compression = None      # Sem compressão
                
                if compression == 'jpeg' and img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                save_kwargs = {'format': 'TIFF'}
                if compression:
                    save_kwargs['compression'] = compression
                    if compression == 'jpeg':
                        save_kwargs['quality'] = quality
                
                img.save(output, **save_kwargs)
                print(f"TIFF salvo com compressão: {compression}, qualidade: {quality}")
                
            else:
                # Formato genérico
                img.save(output, format=output_format.upper())
                print(f"Formato {output_format} salvo sem compressão específica")
                
            mimetype = f'image/{output_format}'
            ext = output_format

        output.seek(0)
        final_size = len(output.getvalue())
        
        # Nome do arquivo de saída
        filename_base = os.path.splitext(file.filename)[0]
        output_filename = f'{filename_base}_vetorizado_q{quality}.{ext}'
        
        print(f"=== RESULTADO ===")
        print(f"Arquivo final: {output_filename}")
        print(f"Tamanho final: {final_size} bytes ({final_size/1024/1024:.2f} MB)")
        print(f"Qualidade aplicada: {quality}")
        
        return send_file(
            output,
            mimetype=mimetype,
            download_name=output_filename,
            as_attachment=True
        )
        
    except Exception as e:
        print(f"ERRO DETALHADO: {str(e)}")
        import traceback
        traceback.print_exc()
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
