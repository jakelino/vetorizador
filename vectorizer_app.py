import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import sys

class VetorizadorAvancado:
    def __init__(self, root):
        self.root = root
        self.root.title('Vetorizador Profissional')
        self.root.geometry('600x650')
        
        self.image_path = None
        self.output_path = None
        
        # Configuração do layout principal
        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Seção de seleção de arquivo
        file_frame = tk.LabelFrame(main_frame, text='Controle de Arquivo')
        file_frame.pack(fill=tk.X, pady=5)
        
        self.btn_selecionar = tk.Button(file_frame, text='Selecionar Imagem', command=self.selecionar_imagem)
        self.btn_selecionar.pack(side=tk.LEFT, padx=5)
        
        self.lbl_status = tk.Label(file_frame, text='Nenhum arquivo selecionado')
        self.lbl_status.pack(side=tk.LEFT, padx=10)
        
        # Seção de parâmetros de vetorização
        params_frame = tk.LabelFrame(main_frame, text='Parâmetros de Vetorização')
        params_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        # Sliders de configuração
        self.criar_slider(params_frame, 'Limiar de Binarização (0-255):', 0, 255, 128, 'threshold')
        self.criar_slider(params_frame, 'Opacidade Mínima (%):', 0, 100, 10, 'opacity')
        self.criar_slider(params_frame, 'Agrupamento Horizontal:', 1, 20, 1, 'grouping')
        self.criar_slider(params_frame, 'Suavização de Bordas:', 0, 10, 0, 'smooth')
        self.criar_slider(params_frame, 'Escala de Saída:', 1, 5, 1, 'scale')
        
        # Seção de formato de saída
        format_frame = tk.LabelFrame(main_frame, text='Configurações de Saída')
        format_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(format_frame, text='Formato:').pack(side=tk.LEFT)
        self.formato_saida = ttk.Combobox(format_frame, values=['SVG', 'PNG', 'PDF', 'EPS'])
        self.formato_saida.current(0)
        self.formato_saida.pack(side=tk.LEFT, padx=5)
        
        tk.Label(format_frame, text='Cor de Fundo:').pack(side=tk.LEFT, padx=(10,0))
        self.cor_fundo = tk.Entry(format_frame, width=7)
        self.cor_fundo.insert(0, '#FFFFFF')
        self.cor_fundo.pack(side=tk.LEFT)
        
        # Botão de processamento
        self.btn_vetorizar = tk.Button(main_frame, text='Vetorizar Imagem', 
                                     command=self.vetorizar_imagem, state=tk.DISABLED)
        self.btn_vetorizar.pack(pady=10)

    def criar_slider(self, frame, texto, de, para, padrao, var_name):
        container = tk.Frame(frame)
        container.pack(fill=tk.X, pady=2)
        
        label = tk.Label(container, text=texto)
        label.pack(side=tk.LEFT, anchor='w')
        
        slider = tk.Scale(container, from_=de, to=para, orient=tk.HORIZONTAL)
        slider.set(padrao)
        slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        setattr(self, var_name, slider)

    def selecionar_imagem(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[('Imagens', '*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.webp')])
        if self.image_path:
            nome_arquivo = os.path.basename(self.image_path)
            self.lbl_status.config(text=nome_arquivo)
            self.btn_vetorizar.config(state=tk.NORMAL)

    def vetorizar_imagem(self):
        try:
            # Coletar parâmetros
            params = {
                'threshold': self.threshold.get(),
                'opacity': self.opacity.get() / 100,
                'grouping': self.grouping.get(),
                'smooth': self.smooth.get(),
                'scale': self.scale.get(),
                'bg_color': self.cor_fundo.get(),
                'format': self.formato_saida.get().lower()
            }
            
            # Processar imagem
            self.output_path = self.processar_imagem(params)
            
            # Mostrar resultado
            self.mostrar_resultado()
            
        except Exception as e:
            messagebox.showerror('Erro', f'Falha na vetorização:\n{str(e)}')

    def processar_imagem(self, params):
        img = Image.open(self.image_path).convert('RGBA')
        width, height = img.size
        
        # Aplicar escala
        if params['scale'] > 1:
            img = img.resize((width*params['scale'], height*params['scale']), Image.NEAREST)
        
        # Processar de acordo com o formato
        if params['format'] == 'svg':
            return self.gerar_svg(img, params)
        else:
            return self.gerar_outros_formatos(img, params)

    def gerar_svg(self, img, params):
        svg_content = self.gerar_svg_content(img, params)
        output_path = self.gerar_nome_arquivo('svg')
        with open(output_path, 'w') as f:
            f.write(svg_content)
        return output_path

    def gerar_svg_content(self, img, params):
        width, height = img.size
        pixels = img.load()
        svg_elements = []
        
        for y in range(height):
            x = 0
            while x < width:
                r, g, b, a = pixels[x, y]
                if a < int(params['opacity'] * 255):
                    x += 1
                    continue
                
                # Agrupamento de pixels
                start_x = x
                while x < width and pixels[x, y] == (r, g, b, a):
                    x += 1
                    if (x - start_x) >= params['grouping']:
                        break
                
                # Adicionar elemento SVG
                svg_elements.append(
                    f'<rect x="{start_x}" y="{y}" width="{x - start_x}" height="1" '
                    f'fill="#{r:02x}{g:02x}{b:02x}" fill-opacity="{a/255:.2f}"/>'
                )
        
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'style="background:{params["bg_color"]}" shape-rendering="crispEdges">\n'
            + '\n'.join(svg_elements) + '\n</svg>'
        )

    def gerar_outros_formatos(self, img, params):
        output_path = self.gerar_nome_arquivo(self.formato_saida.get().lower())
        img.save(output_path)
        return output_path

    def gerar_nome_arquivo(self, extensao):
        base = os.path.splitext(self.image_path)[0]
        return f'{base}_vetorizado.{extensao}'

    def mostrar_resultado(self):
        resposta = messagebox.askyesno(
            'Concluído',
            f'Arquivo salvo em:\n{self.output_path}\n\nDeseja abrir o arquivo?'
        )
        if resposta:
            self.abrir_arquivo()

    def abrir_arquivo(self):
        try:
            if sys.platform == 'win32':
                os.startfile(self.output_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{self.output_path}"')
            else:
                os.system(f'xdg-open "{self.output_path}"')
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível abrir o arquivo:\n{str(e)}')

if __name__ == '__main__':
    root = tk.Tk()
    app = VetorizadorAvancado(root)
    root.mainloop()
