from flask import Blueprint, request, jsonify
import json
import os

mcs_bp = Blueprint('mcs', __name__)

# ملف التخزين الموحد
DATA_FILE = 'mcs_data.json'

# المتغيرات الداخلية
server_variables = {
    "text01": "mcsadmin202224",
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

# بيانات النافذة المنبثقة
popup_data = {
    "image_path": "",
    "text": "",
    "status": "off"
}

# بيانات الأخبار
news_data = []

# بيانات إصدارات التحميل
downloads_data = [
    {
        "id": 1,
        "image_path": "test.jpeg",
        "text": "تجربة",
        "download_url": "sss.ss"
    },
    {
        "id": 2,
        "image_path": "test2.jpeg",
        "text": "تجربة 2",
        "download_url": "sss2.ss"
    }
]

# تهيئة البيانات الافتراضية
def init_default_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            global popup_data, news_data, downloads_data
            popup_data = data.get("popup", popup_data)
            news_data = data.get("news", news_data)
            downloads_data = data.get("downloads", downloads_data)
    else:
        data = {
            "popup": popup_data,
            "news": news_data,
            "downloads": downloads_data
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# دالة لحفظ جميع البيانات
def save_all_data():
    data = {
        "popup": popup_data,
        "news": news_data,
        "downloads": downloads_data
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تهيئة البيانات عند استيراد الملف
init_default_data()

# APIs لإدارة النافذة المنبثقة
@mcs_bp.route('/popup', methods=['GET'])
def get_popup():
    """الحصول على بيانات النافذة المنبثقة"""
    return jsonify(popup_data)

@mcs_bp.route('/popup', methods=['POST'])
def update_popup():
    """تحديث بيانات النافذة المنبثقة"""
    global popup_data
    popup_data = request.get_json()
    save_all_data()
    return jsonify({"message": "تم حفظ بيانات النافذة المنبثقة بنجاح"})


# APIs لإدارة الأخبار
@mcs_bp.route('/news', methods=['GET'])
def get_news():
    """الحصول على جميع الأخبار"""
    return jsonify(news_data)

@mcs_bp.route('/news', methods=['POST'])
def add_news():
    """إضافة خبر جديد"""
    global news_data
    news_item = request.get_json()
    new_news = {
        "id": len(news_data) + 1,
        "image_path": news_item.get('image_path', ''),
        "text": news_item.get('text', '')
    }
    news_data.append(new_news)
    save_all_data()
    return jsonify({"message": "تم إضافة الخبر بنجاح", "id": new_news["id"]})

@mcs_bp.route('/news/<int:news_id>', methods=['PUT'])
def update_news(news_id):
    """تحديث خبر محدد"""
    global news_data
    news_item = request.get_json()
    for news in news_data:
        if news["id"] == news_id:
            news["image_path"] = news_item.get('image_path', news["image_path"])
            news["text"] = news_item.get('text', news["text"])
            save_all_data()
            return jsonify({"message": f"تم تحديث الخبر رقم {news_id} بنجاح"})
    return jsonify({"error": "الخبر غير موجود"}), 404

@mcs_bp.route('/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    """حذف خبر محدد"""
    global news_data
    for i, news in enumerate(news_data):
        if news["id"] == news_id:
            del news_data[i]
            save_all_data()
            return jsonify({"message": f"تم حذف الخبر رقم {news_id} بنجاح"})
    return jsonify({"error": "الخبر غير موجود"}), 404

# APIs لإدارة التحميل
@mcs_bp.route('/download', methods=['GET'])
def get_downloads():
    """الحصول على جميع إصدارات التحميل"""
    return jsonify(downloads_data)

@mcs_bp.route('/download', methods=['POST'])
def add_download():
    """إضافة إصدار جديد"""
    global downloads_data
    download_item = request.get_json()
    new_download = {
        "id": len(downloads_data) + 1,
        "image_path": download_item.get('image_path', ''),
        "text": download_item.get('text', ''),
        "download_url": download_item.get('download_url', '')
    }
    downloads_data.append(new_download)
    save_all_data()
    return jsonify({"message": "تم إضافة الإصدار بنجاح", "id": new_download["id"]})

@mcs_bp.route('/download/<int:download_id>', methods=['PUT'])
def update_download(download_id):
    """تحديث إصدار محدد"""
    global downloads_data
    download_item = request.get_json()
    for download in downloads_data:
        if download["id"] == download_id:
            download["image_path"] = download_item.get('image_path', download["image_path"])
            download["text"] = download_item.get('text', download["text"])
            download["download_url"] = download_item.get('download_url', download["download_url"])
            save_all_data()
            return jsonify({"message": f"تم تحديث الإصدار رقم {download_id} بنجاح"})
    return jsonify({"error": "الإصدار غير موجود"}), 404

@mcs_bp.route('/download/<int:download_id>', methods=['DELETE'])
def delete_download(download_id):
    """حذف إصدار محدد"""
    global downloads_data
    for i, download in enumerate(downloads_data):
        if download["id"] == download_id:
            del downloads_data[i]
            save_all_data()
            return jsonify({"message": f"تم حذف الإصدار رقم {download_id} بنجاح"})
    return jsonify({"error": "الإصدار غير موجود"}), 404

# APIs لإدارة المتغيرات الداخلية
@mcs_bp.route('/variables', methods=['GET'])
def get_variables():
    """الحصول على جميع المتغيرات الداخلية"""
    return jsonify(server_variables)

@mcs_bp.route('/variables/<variable_name>', methods=['GET'])
def get_variable(variable_name):
    """الحصول على متغير محدد"""
    if variable_name in server_variables:
        return jsonify({variable_name: server_variables[variable_name]})
    return jsonify({"error": "المتغير غير موجود"}), 404

@mcs_bp.route('/variables/<variable_name>', methods=['POST'])
def set_variable(variable_name):
    """تحديث متغير محدد"""
    data = request.get_json()
    if variable_name in server_variables:
        server_variables[variable_name] = data.get('value', '')
        return jsonify({"message": f"تم تحديث المتغير {variable_name} بنجاح"})
    return jsonify({"error": "المتغير غير موجود"}), 404

# صفحة الاختبار للتأكد من عمل قسم MCS
@mcs_bp.route('/')
def mcs_home():
    return jsonify({
        "message": "قسم MCS يعمل بنجاح",
        "endpoints": {
            "p": {
                "ge": "/p",
                "po": "/p"
            },
            "n": {
                "ge": "/n",
                "po": "/n",
                "p": "/n/<id>",
                "d": "/n/<id>"
            },
            "d": {
                "ge": "/d",
                "po": "/d",
                "p": "/d/<id>",
                "d": "/d/<id>"
            },
            "v": {
                "ve_all": "/vs",
                "ve_one": "/vs/<name>",
            }
        }
    })