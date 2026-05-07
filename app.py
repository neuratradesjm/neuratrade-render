from flask import Flask, jsonify, send_from_directory
import random
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    # Lógica de Neura Trade: Profit entre 2% y 4.5% menos $5 de comisión
    profit_pct = random.uniform(0.02, 0.045)
    commission = 5.00
    return jsonify({
        "status": "success",
        "profit_pct": round(profit_pct * 100, 2),
        "commission": commission,
        "server_time": "Render Cloud Active"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
