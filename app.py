from flask import Flask, jsonify, send_from_directory
import random
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    pares = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]
    par_elegido = random.choice(pares)
    profit_pct = random.uniform(0.015, 0.042)
    comision = 5.00
    
    return jsonify({
        "status": "success",
        "par": par_elegido,
        "profit_pct": round(profit_pct * 100, 2),
        "comision": comision,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "id_operacion": f"TX-{random.randint(1000, 9999)}"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
