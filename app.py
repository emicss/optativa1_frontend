from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# URL construida con los datos de tu captura (Asegúrate de que 'v1' sea tu etapa)
AWS_API_URL = "https://zu3g6t4634.execute-api.us-east-1.amazonaws.com/v1/datos" 

@app.route('/')
def inicio():
    try:
        # Hace un GET sin ID para traer toda la lista gracias al scan()
        response = requests.get(AWS_API_URL)
        datos = response.json()
        
        # Si por alguna razón no es una lista, mandamos un arreglo vacío para no romper la vista
        if not isinstance(datos, list):
            datos = []
    except Exception as e:
        print(f"Error conectando a AWS: {e}")
        datos = []
        
    return render_template('lista.html', items=datos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nuevo_id = request.form.get('id')
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        
        payload = {"id": nuevo_id, "titulo": titulo, "autor": autor}
        requests.post(AWS_API_URL, json=payload)
        
        return redirect(url_for('inicio'))
        
    return render_template('formulario.html', item=None)

@app.route('/modificar/<id>', methods=['GET', 'POST'])
def modificar(id):
    if request.method == 'POST':
        titulo_modificado = request.form.get('titulo')
        autor_modificado = request.form.get('autor')
        
        payload = {"id": id, "titulo": titulo_modificado, "autor": autor_modificado}
        requests.put(AWS_API_URL, json=payload)
        
        return redirect(url_for('inicio'))
        
    # Hace un GET pasando el ID para pre-llenar los campos del formulario
    response = requests.get(f"{AWS_API_URL}?id={id}")
    item_actual = response.json() if response.status_code == 200 else None
    
    return render_template('formulario.html', item=item_actual)

@app.route('/eliminar/<id>')
def eliminar(id):
    payload = {"id": id}
    requests.delete(AWS_API_URL, json=payload)
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)