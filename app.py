from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# --- NEURA TRADE CONFIGURATION ---
# Estas llaves permiten la conexión con Binance para generar tus beneficios.
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7TohnOG5dMBaiZQ7lqRPgmJ904XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs21JtjxkMw2wrn2jftheE3g3vvNoqrhw20jtEcno99RQ8Xv86u'

@app.route('/')
def index():
    try:
        # Carga la interfaz de Neura Trade que se ve en tu captura.
        return render_template('index.html')
    except Exception as e:
        return f"Error: index.html not found. {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Los nombres 'usuario' y 'password' coinciden con tu formulario.
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        # Validación para acceder al dashboard de Neura Trade.
        if usuario == 'admin' and password == 'admin1234':
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
            
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except:
        return "Dashboard logic active. Template file missing."

@app.route('/registro')
def registro():
    try:
        return render_template('registro.html')
    except:
        return "Registration page logic active."

if __name__ == '__main__':
    # Configuración de puerto necesaria para que Render no falle.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
