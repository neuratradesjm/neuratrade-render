from flask import Flask, jsonify, render_template, request, session, redirect, send_from_directory
import random
import os
import psycopg2
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'neura_trade_key_2026_secure'

# --- Gestión de Base de Datos ---
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    result = urlparse(db_url)
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Tabla de Usuarios de Neura Trade
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id serial PRIMARY KEY,
                username varchar(50) UNIQUE NOT NULL,
                password varchar(100) NOT NULL,
                balance float DEFAULT 1250.00,
                created_at timestamp DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        # Tabla de Operaciones vinculada por user_id
        cur.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id serial PRIMARY KEY,
                user_id integer,
                trade_id varchar(20),
                pair varchar(10),
                profit float,
                date timestamp DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inicializando Neura DB: {e}")

init_db()

# --- Rutas de Navegación ---

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- APIs de Usuario ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    user = data.get('user')
    password = data.get('pass')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (user, password))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Registro en Neura Trade exitoso"})
    except:
        return jsonify({"status": "error", "message": "El usuario ya existe"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = data.get('user')
    password = data.get('pass')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username FROM users WHERE username = %s AND password = %s', (user, password))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        if user_data:
            session['user_id'] = user_data[0]
            session['username'] = user_data[1]
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Credenciales incorrectas"})
    except:
        return jsonify({"status": "error", "message": "Error de conexión"})

# --- APIs de Trading ---

@app.route('/api/get-balance', methods=['GET'])
def get_balance():
    user_id = session.get('user_id')
    balance_inicial = 1250.00
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT SUM(profit) FROM trades WHERE user_id = %s', (user_id,))
        res = cur.fetchone()[0]
        total_profit = res if res else 0
        cur.close()
        conn.close()
        balance_actual = balance_inicial + (balance_inicial * (total_profit / 100))
        return jsonify({"status": "success", "balance": round(balance_actual, 2)})
    except:
        return jsonify({"status": "error", "balance": balance_inicial})

@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    user_id = session.get('user_id')
    pares = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]
    par_elegido = random.choice(pares)
    profit_pct = round(random.uniform(1.5, 4.2), 2)
    id_transaccion = f"TX-{random.randint(1000, 9999)}"
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO trades (user_id, trade_id, pair, profit) VALUES (%s, %s, %s, %s)', 
                    (user_id, id_transaccion, par_elegido, profit_pct))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)
    return jsonify({"status": "success", "par": par_elegido, "profit_pct": profit_pct, 
                    "timestamp": datetime.now().strftime("%H:%M:%S"), "id_operacion": id_transaccion})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
