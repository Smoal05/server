from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from room import room_bp
from mcs import mcs_bp
from login import login_bp
import os
import time
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# تخزين سجل الطلبات
request_logs = []
MAX_LOGS = 1000

# middleware لتسجيل الطلبات
@app.before_request
def log_request():
    if request.path != '/health' and not request.path.startswith('/static'):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        request_logs.append(log_entry)
        if len(request_logs) > MAX_LOGS:
            request_logs.pop(0)

# تسجيل النقاط (Blueprints)
app.register_blueprint(room_bp, url_prefix='/room')
app.register_blueprint(mcs_bp, url_prefix='/mcs')
app.register_blueprint(login_bp, url_prefix='/login')

@app.route('/lol')
def home():
    return jsonify({
        "message": "مرحباً بك في السيرفر الجديد",
        "endpoints": {
            "rooms": "/room",
            "mcs": "/mcs", 
            "login": "/login",
            "dashboard": "/dashboard01"
        }
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "main server",
        "timestamp": datetime.now().isoformat(),
        "uptime": get_uptime()
    })

@app.route('/dashboard01s')
def dashboard():
    """لوحة التحكم الرئيسية"""
    return render_template('control.html')

@app.route('/api/logs')
def get_logs():
    """الحصول على سجل الطلبات"""
    return jsonify({
        "logs": request_logs[-100:],  # آخر 100 طلب
        "total": len(request_logs)
    })

@app.route('/api/stats')
def get_stats():
    """إحصائيات السيرفر"""
    return jsonify({
        "uptime": get_uptime(),
        "total_requests": len(request_logs),
        "active_rooms": get_active_rooms_count(),
        "memory_usage": get_memory_usage(),
        "timestamp": datetime.now().isoformat()
    })

def get_uptime():
    """حساب مدة تشغيل السيرفر"""
    return time.time() - app.start_time

def get_active_rooms_count():
    """عدد الغرف النشطة"""
    try:
        from room import rooms
        return len(rooms)
    except:
        return 0

def get_memory_usage():
    """استخدام الذاكرة"""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # MB

if __name__ == '__main__':
    app.start_time = time.time()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)