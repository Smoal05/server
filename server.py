from flask import Flask, jsonify
from flask_cors import CORS
from room import room_bp
from mcs import mcs_bp
from login import login_bp

import os

app = Flask(__name__)
CORS(app)

# تسجيل النقاط (Blueprints)
app.register_blueprint(room_bp, url_prefix='/room')

app.register_blueprint(mcs_bp, url_prefix='/mcs')

app.register_blueprint(login_bp, url_prefix='/login')


@app.route('/')
def home():
    return jsonify({
        "message": "مرحباً بك في السيرفر",
       
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "main server"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)