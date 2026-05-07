from flask import Flask, jsonify, render_template, request, session, redirect
# ... (mantén tus otros imports de psycopg2 y random) ...

app.secret_key = 'neura_trade_key_2026' # Clave para sesiones seguras

# Ruta para la Landing Page Corporativa
@app.route('/')
def home():
    return render_template('landing.html')

# Ruta para el Dashboard (Protegido)
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return send_from_directory(app.static_folder, 'index.html')

# API de Login Simple
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # Por ahora validación simple, luego conectaremos con DB
    if data.get('user') == 'admin' and data.get('pass') == 'neura2026':
        session['user'] = 'admin'
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Credenciales inválidas"})
