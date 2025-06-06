from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}

def allowed_file(filename):                                                                                        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'Nenhum arquivo enviado'}, 400
        
    file = request.files['file']
    output_format = request.form.get('format', 'png').lower()
    
    if file and allowed_file(file.filename):
        try:
            # Processar imagem
            img = Image.open(file.stream).convert('RGBA')
            width, height = img.size
            
            # Vetorização básica (binarização)
            threshold = 128
            img_processed = img.convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
            
            # Preparar saída
            output = io.BytesIO()
            
            if output_format == 'svg':
                # Gerar SVG otimizado
                svg_content = self.gerar_svg(img_processed)
                output.write(svg_content.encode('utf-8'))
                mimetype = 'image/svg+xml'
                ext = 'svg'
            else:
                img_processed.save(output, format=output_format.upper())
                mimetype = f'image/{output_format}'
                ext = output_format
            
            output.seek(0)
            
            # Nome do arquivo de saída
            filename_base = os.path.splitext(file.filename)[0]
            output_filename = f'{filename_base}_vetorizado.{ext}'
            
            return send_file(
                output,
                mimetype=mimetype,
                download_name=output_filename
            )
            
        except Exception as e:
            return {'error': f'Erro no processamento: {str(e)}'}, 500
    
    return {'error': 'Tipo de arquivo não permitido'}, 400

def gerar_svg(img):
    width, height = img.size
    svg_elements = []
    
    for y in range(height):
        x = 0
        while x < width:
            pixel = img.getpixel((x, y))
            if pixel == 0:  # Pixel preto
                start_x = x
                while x < width and img.getpixel((x, y)) == 0:
                    x += 1
                width_rect = x - start_x
                svg_elements.append(
                    f'<rect x="{start_x}" y="{y}" width="{width_rect}" height="1" fill="#000000"/>'
                )
            else:
                x += 1
    
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'shape-rendering="crispEdges">\n'
        + '\n'.join(svg_elements) + '\n</svg>'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
