from flask import Flask, render_template, request, send_file
import os
import shutil
from werkzeug.utils import secure_filename
from generator import build_pdf

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate():
    # Procesar Logo
    logo = request.files.get('logo')
    logo_path = ""
    if logo:
        logo_path = os.path.join(UPLOAD_FOLDER, secure_filename(logo.filename))
        logo.save(logo_path)

    # Capturar listas
    descripciones = request.form.getlist('descripcion[]')
    cantidades = request.form.getlist('cantidad[]')
    montos = request.form.getlist('monto[]')
    imagenes = request.files.getlist('item_img[]')

    items_data = []
    for i in range(len(descripciones)):
        img_path = ""
        if i < len(imagenes) and imagenes[i].filename != '':
            img_path = os.path.join(UPLOAD_FOLDER, f"item_{i}_" + secure_filename(imagenes[i].filename))
            imagenes[i].save(img_path)
            
        items_data.append({
            'desc': descripciones[i],
            'cant': float(cantidades[i] or 0),
            'monto': float(montos[i] or 0),
            'img': img_path
        })

    full_data = {
        'empresa': request.form.get('empresa', 'Presupuesto'),
        'emision': request.form.get('fecha_emision'),
        'vencimiento': request.form.get('fecha_vencimiento'),
        'logo': logo_path,
        'items': items_data
    }

    pdf_name = "presupuesto.pdf"
    build_pdf(pdf_name, full_data)
    
    return send_file(pdf_name, as_attachment=True)

@app.after_request
def cleanup(response):
    # Definimos la ruta de la carpeta de subidas
    folder = app.config['UPLOAD_FOLDER']
    
    # Recorremos los archivos y los borramos uno por uno
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) # Borra archivos
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path) # Borra carpetas si las hubiera
        except Exception as e:
            print(f'Error al borrar {file_path}: {e}')
            
    return response

if __name__ == '__main__':
    app.run(debug=True)