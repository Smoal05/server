from flask import Blueprint, request, jsonify


login_bp = Blueprint('login', __name__)

# المتغيرات الداخلية (10 متغيرات)
server_variables = {
    "mcs_login": "mcsadmin202224",  # كلمة المرور الافتراضية
    "text02": "",
    "text03": "",
    "text04": "",
    "text05": "",
    "status01": "off",
    "status02": "off",
    "status03": "off",
    "counter01": 0,
    "counter02": 0
}
# API للتحقق من كلمة المرور
@login_bp.route('/login/check-password', methods=['POST'])
def check_password():
    """التحقق من كلمة المرور"""
    data = request.get_json()
    entered_password = data.get('password', '')
    
    # المقارنة مع المتغير text01 في السيرفر
    if entered_password == server_variables['mcs_login']:
        return jsonify({"success": True, "message": "تم التحقق بنجاح"})
    else:
        return jsonify({"success": False, "message": "كلمة المرور غير صحيحة"}), 401
