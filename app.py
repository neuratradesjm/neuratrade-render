from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE BINANCE (NEURA TRADE) ---
# Se mantiene la configuración exacta que verificamos anteriormente
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7TohnOG5dMBaiZQ7lqRPgmJ904XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs21JtjxkMw2wrn2jftheE3g3vvNoqrhw20jtEcno99RQ8Xv86u'

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    # Carga la landing page con el diseño de Neura Trade
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        # Validación de acceso para el administrador
        if usuario == 'admin' and password == 'admin1234':
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Credenciales incorrectas")
            
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Aquí se visualizan los beneficios proporcionales de los usuarios y tus comisiones
    return render_template('dashboard.html')

@app.route('/registro')
def registro():
    # Ruta para el botón de registro que solicitaste mantener
    return render_template('registro.html')

if __name__ == '__main__':
    # Configuración de puerto para Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
