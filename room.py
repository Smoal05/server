from flask import Blueprint, request, jsonify
import threading

room_bp = Blueprint('room', __name__)

lock = threading.Lock()
# مخزن الغرف في الذاكرة فقط: rooms[name] = "max/current"  مثل "6/1"
rooms = {}

@room_bp.route('/', methods=['GET', 'POST'])
def handle_room():
    if request.method == 'GET':
        # إرجاع جميع الغرف
        with lock:
            return jsonify({"status": "running", "rooms_active": len(rooms), "rooms": rooms})
    else:
        # POST - معالجة الإجراءات المختلفة
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        action = data.get('action', '').lower()

        # FIND -> لا يغيّر عدد اللاعبين، فقط يعيد اسم غرفة متاحة إن وُجدت
        if action == "find":
            with lock:
                for name, status in rooms.items():
                    try:
                        max_p, cur = map(int, status.split("/"))
                    except Exception:
                        continue
                    if cur < max_p:
                        return jsonify({"Existing": True, "room_name": name})
            return jsonify({"Existing": False})

        # CREATE -> تسجّل الغرفة التي أنشأتها اللعبة محلياً
        elif action == "create":
            room_name = data.get('room_name')
            players = data.get('players')
            if not room_name or not players:
                return jsonify({"error": "room_name and players required for create"}), 400
            with lock:
                rooms[room_name] = players
            return jsonify({"Created": True, "room_name": room_name, "players": players})

        # JOIN -> زيادة عدد اللاعبين لغرفة محددة بمقدار 1، وحذفها إذا امتلأت
        elif action == "join":
            room_name = data.get('room_name')
            if not room_name:
                return jsonify({"error": "room_name required for join"}), 400
            with lock:
                if room_name not in rooms:
                    return jsonify({"error": "room_not_found"}), 404
                try:
                    max_p, cur = map(int, rooms[room_name].split("/"))
                except Exception:
                    return jsonify({"error": "invalid_room_format"}), 400
                cur += 1
                removed = False
                if cur >= max_p:
                    # إذا وصل أو تجاوز الحد نحذف الغرفة من القوائم
                    del rooms[room_name]
                    removed = True
                else:
                    rooms[room_name] = f"{max_p}/{cur}"
            return jsonify({"joined": True, "room_name": room_name, "current": cur, "removed": removed})

        # LEAVE -> تقليل عدد اللاعبين
        elif action == "leave":
            room_name = data.get('room_name')
            if not room_name:
                return jsonify({"error": "room_name required for leave"}), 400
            with lock:
                if room_name not in rooms:
                    return jsonify({"error": "room_not_found"}), 404
                try:
                    max_p, cur = map(int, rooms[room_name].split("/"))
                except Exception:
                    return jsonify({"error": "invalid_room_format"}), 400
                cur = max(cur - 1, 0)
                if cur == 0:
                    del rooms[room_name]
                else:
                    rooms[room_name] = f"{max_p}/{cur}"
            return jsonify({"left": True, "room_name": room_name, "current": cur})

        # DELETE -> حذف الغرفة
        elif action == "delete":
            room_name = data.get('room_name')
            with lock:
                # لو ذكر اسم الغرفة: نحذفها مباشرة
                if room_name:
                    if room_name not in rooms:
                        return jsonify({"error": "room_not_found"}), 404
                    del rooms[room_name]
                    return jsonify({"deleted": True, "room_name": room_name})
                # لو ما ذكرش اسم: نحذف أول غرفة موجودة
                if not rooms:
                    return jsonify({"error": "no_rooms"}), 404
                first_room = next(iter(rooms))
                del rooms[first_room]
                return jsonify({"deleted": True, "room_name": first_room})

        else:
            return jsonify({"error": "unknown action"}), 400

# endpoint إضافي لعرض جميع الغرف
@room_bp.route('/all', methods=['GET'])
def get_all_rooms():
    with lock:
        return jsonify({"rooms": rooms, "count": len(rooms)})