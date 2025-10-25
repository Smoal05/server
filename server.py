# server.py (مُحدَّث مع CORS)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
import threading

# إضافة CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CORS middleware ---
# أثناء التطوير: سمحنا لكل الأصول حتى لا تواجه مشاكل عند التجريب من الهاتف أو من استضافة ثابتة
# لاحقًا في الإنتاج غيّر allow_origins إلى قائمة النطاقات الموثوقة فقط، مثلاً:
# allow_origins=["https://dashboard.example.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # للتطوير: اترك "*" أو ضع قائمة محددة للإنتاج
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------

lock = threading.Lock()
# مخزن الغرف في الذاكرة فقط: rooms[name] = "max/current"  مثل "6/1"
rooms: Dict[str, str] = {}

class RoomRequest(BaseModel):
    action: str                 # "find", "create", "join", "leave", "delete"
    room_name: Optional[str] = None
    players: Optional[str] = None  # مثل "6/1"

@app.get("/")
def root():
    return {"status": "running", "rooms_active": len(rooms)}

# Endpoint لفحص جميع الغرف (مفيد للتطوير والاختبار)
@app.get("/rooms")
def get_rooms():
    # نعيد نسخة من القوائم حتى لا نعرض مرجعية قابلة للتعديل
    with lock:
        return {"rooms": dict(rooms)}

@app.post("/room")
def handle_room(req: RoomRequest):
    global rooms
    action = req.action.lower()

    # FIND -> لا يغيّر عدد اللاعبين، فقط يعيد اسم غرفة متاحة إن وُجدت
    if action == "find":
        with lock:
            for name, status in rooms.items():
                try:
                    max_p, cur = map(int, status.split("/"))
                except Exception:
                    continue
                if cur < max_p:
                    # نُعيد اسم الغرفة لكن لا نعدّلها هنا
                    return {"Existing": True, "room_name": name}
        return {"Existing": False}

    # CREATE -> تسجّل الغرفة التي أنشأتها اللعبة محلياً
    elif action == "create":
        if not req.room_name or not req.players:
            return {"error": "room_name and players required for create"}
        with lock:
            rooms[req.room_name] = req.players
        return {"Created": True, "room_name": req.room_name, "players": req.players}

    # JOIN -> زيادة عدد اللاعبين لغرفة محددة بمقدار 1، وحذفها إذا امتلأت
    elif action == "join":
        if not req.room_name:
            return {"error": "room_name required for join"}
        with lock:
            if req.room_name not in rooms:
                return {"error": "room_not_found"}
            try:
                max_p, cur = map(int, rooms[req.room_name].split("/"))
            except Exception:
                return {"error": "invalid_room_format"}
            cur += 1
            removed = False
            if cur >= max_p:
                # إذا وصل أو تجاوز الحد نحذف الغرفة من القوائم
                del rooms[req.room_name]
                removed = True
            else:
                rooms[req.room_name] = f"{max_p}/{cur}"
        return {"joined": True, "room_name": req.room_name, "current": cur, "removed": removed}

    # LEAVE -> إن أردت تقليل عدد اللاعبين (ليس مطلوب الآن لكن مفيد)
    elif action == "leave":
        if not req.room_name:
            return {"error": "room_name required for leave"}
        with lock:
            if req.room_name not in rooms:
                return {"error": "room_not_found"}
            try:
                max_p, cur = map(int, rooms[req.room_name].split("/"))
            except Exception:
                return {"error": "invalid_room_format"}
            cur = max(cur - 1, 0)
            if cur == 0:
                del rooms[req.room_name]
            else:
                rooms[req.room_name] = f"{max_p}/{cur}"
        return {"left": True, "room_name": req.room_name, "current": cur}

    # DELETE -> حذف الغرفة صراحة، أو حذف أول غرفة موجودة مهما كانت حالتها لو ما ذُكر اسم
    elif action == "delete":
        with lock:
            # لو ذكر اسم الغرفة: نحذفها مباشرة
            if req.room_name:
                if req.room_name not in rooms:
                    return {"error": "room_not_found"}
                del rooms[req.room_name]
                return {"deleted": True, "room_name": req.room_name}
            # لو ما ذكرش اسم: نحذف أول غرفة موجودة مهما كانت حالتها
            if not rooms:
                return {"error": "no_rooms"}
            first_room = next(iter(rooms))
            del rooms[first_room]
            return {"deleted": True, "room_name": first_room}

    else:
        return {"error": "unknown action"}