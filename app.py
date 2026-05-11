from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta_neura_2026' # Cambia esto por un string aleatorio

# --- Configuración de Flask-Mail (Ejemplo con Gmail) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu_correo@gmail.com' # Tu correo de empresa
app.config['MAIL_PASSWORD'] = 'tu_contraseña_de_aplicacion' 
mail = Mail(app)

# --- DECORADOR DE SEGURIDAD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debes iniciar sesión para acceder a esta sección.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aquí iría tu lógica de verificación en DB
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'neura2026':
            session['user_id'] = 1
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciales incorrectas", "danger")
    return render_template('login.html')

# --- RUTA PROTEGIDA ---
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

# --- RECUPERACIÓN DE CONTRASEÑA ---
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Lógica para generar token y enviar correo
        msg = Message("Recuperación de Contraseña - Neura Trade",
                      sender="tu_correo@gmail.com",
                      recipients=[email])
        msg.body = "Hola, haz clic en el siguiente enlace para restablecer tu clave: [Enlace de prueba]"
        # mail.send(msg) # Descomentar cuando configures tus credenciales reales
        flash("Se ha enviado un correo con las instrucciones.", "info")
        return redirect(url_for('login'))
    return render_template('reset_password.html')

if __name__ == '__main__':
    app.run(debug=True)
