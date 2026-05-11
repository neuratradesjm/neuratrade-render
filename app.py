from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from functools import wraps
import random
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD ---
app.secret_key = 'neura_trade_ultra_secret_key_2026'

# --- CONFIGURACIÓN DE COMISIONES NEURA TRADE ---
COMISION_BOT_FIJA = 0.50          # Tarifa base por operación
PORCENTAJE_GANANCIA_ADMIN = 0.20  # Tu beneficio: 20% del profit del usuario

# --- CONFIGURACIÓN DE CORREO ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu_correo@gmail.com' 
app.config['MAIL_PASSWORD'] = 'tu_clave_de_aplicacion'
mail = Mail(app)

# --- DECORADOR DE SEGURIDAD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Acceso restringido. Por favor inicia sesión.", "warning")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS ---

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Credenciales de acceso validadas
    if username == 'admin' and password == 'neura2026':
        session.clear()
        session['user_id'] = 1
        session['username'] = 'admin'
        session['balance'] = 1000.00
        session['profit_total'] = 0.0
        session['comisiones_totales'] = 0.0
        return redirect(url_for('dashboard'))
    else:
        flash("Credenciales incorrectas. Verifique usuario y clave.", "danger")
        return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                           username=session.get('username'),
                           balance=session.get('balance'),
                           profit_diario=session.get('profit_total'),
                           comisiones_pagadas=session.get('comisiones_totales'))

@app.route('/ejecutar_trade', methods=['POST'])
@login_required
def ejecutar_trade():
    balance_actual = session.get('balance', 1000.00)
    variacion = random.uniform(-0.01, 0.03) 
    profit_bruto = balance_actual * variacion
    
    if profit_bruto > 0:
        tu_comision = (profit_bruto * PORCENTAJE_GANANCIA_ADMIN) + COMISION_BOT_FIJA
        profit_neto_usuario = profit_bruto - tu_comision
    else:
        tu_comision = COMISION_BOT_FIJA
        profit_neto_usuario = profit_bruto - tu_comision

    session['balance'] = round(balance_actual + profit_neto_usuario, 2)
    session['profit_total'] = round(profit_neto_usuario, 2)
    session['comisiones_totales'] = round(session.get('comisiones_totales', 0.0) + tu_comision, 2)
    
    flash(f"Operación Tridox completada.", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
