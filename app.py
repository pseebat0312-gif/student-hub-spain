import os
import json
from datetime import datetime, date, timezone
import calendar
from flask import Flask, render_template, request, jsonify
import pytz
from supabase import create_client

app = Flask(__name__)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("环境变量未设置")
ADMIN_EMAIL = "pseebat0312@gmail.com"

@app.route("/")
def index():
    spain_tz = pytz.timezone("Europe/Madrid")
    now_spain = datetime.now(spain_tz)
    china_tz = pytz.timezone("Asia/Shanghai")
    now_china = datetime.now(china_tz)
    today = now_spain.date()
    year = today.year
    days_in_year = 366 if calendar.isleap(year) else 365
    day_of_year = today.timetuple().tm_yday
    days_left = days_in_year - day_of_year
    progress = round((day_of_year / days_in_year) * 100, 1)
    return render_template("home.html", spain_time=now_spain.strftime("%Y-%m-%d %H:%M:%S"), china_time=now_china.strftime("%Y-%m-%d %H:%M:%S"), day_of_year=day_of_year, days_left=days_left, progress=progress, year=year)

@app.route("/school")
def school():
    return render_template("school.html")

@app.route("/ai_detect")
def ai_detect():
    return render_template("ai_detect.html")

@app.route("/affairs")
def affairs():
    return render_template("affairs.html")

@app.route("/market")
def market():
    return render_template("market.html")

@app.route("/community")
def community():
    return render_template("community.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/message")
def message():
    return render_template("message.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/currency")
def currency():
    return render_template("currency.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/reset-password")
def reset_password_page():
    return render_template("reset_password.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/countdown")
def countdown():
    return render_template("countdown.html")

@app.route("/emergency")
def emergency():
    return render_template("emergency.html")

@app.route("/homesick")
def homesick():
    return render_template("homesick.html")

@app.route("/treehole")
def treehole():
    return render_template("treehole.html")

def notify(email, ntype, content, link=""):
    if not supabase or not email:
        return
    try:
        supabase.table("notifications").insert({"user_email": email, "type": ntype, "content": content, "link": link}).execute()
    except Exception as e:
        print("通知失败:", e)

@app.route("/api/notifications")
def api_notifications():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        result = supabase.table("notifications").select("*").eq("user_email", owner).order("created_at", desc=True).limit(100).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/notifications/unread")
def api_notifications_unread():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        result = supabase.table("notifications").select("id").eq("user_email", owner).eq("is_read", False).execute()
        return jsonify({"unread": len(result.data or [])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/notifications/read", methods=["POST"])
def api_notifications_read():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    ids = data.get("ids", [])
    if not ids:
        return jsonify({"success": True})
    try:
        supabase.table("notifications").update({"is_read": True}).in_("id", ids).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset_password", methods=["POST"])
def api_reset_password():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少邮箱"}), 400
    try:
        supabase.auth.reset_password_email(email, {"redirect_to": "https://student-hub-spain.onrender.com/reset-password"})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/update_password", methods=["POST"])
def api_update_password():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    token = data.get("token", "")
    password = data.get("password", "")
    if not token or not password:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.auth.set_session(token, token)
        supabase.auth.update_user({"password": password})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/messages")
def api_messages():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("messages").select("*").eq("is_public", True).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages/mine")
def api_messages_mine():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("messages").select("*").eq("user_email", email).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages/add", methods=["POST"])
def api_messages_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        data = request.get_json()
        email = data.get("email", "").strip() or "anonymous"
        content = data.get("content", "").strip()
        if not content:
            return jsonify({"error": "缺少内容"}), 400
        supabase.table("messages").insert({"user_email": email, "content": content, "is_public": False}).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/messages", methods=["POST"])
def api_admin_messages():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    token = data.get("token", "")
    if not token:
        return jsonify({"error": "未授权"}), 401
    try:
        resp = supabase.auth.get_user(token)
        if resp.user.email != ADMIN_EMAIL:
            return jsonify({"error": "无权限"}), 403
        result = supabase.table("messages").select("*").order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/messages/update", methods=["POST"])
def api_admin_messages_update():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    token = data.get("token", "")
    msg_id = data.get("id")
    updates = data.get("updates", {})
    if not token or not msg_id:
        return jsonify({"error": "缺少参数"}), 400
    try:
        resp = supabase.auth.get_user(token)
        if resp.user.email != ADMIN_EMAIL:
            return jsonify({"error": "无权限"}), 403
        supabase.table("messages").update(updates).eq("id", msg_id).execute()
        try:
            msg = supabase.table("messages").select("user_email, content").eq("id", msg_id).execute()
            if msg.data:
                owner = msg.data[0]["user_email"]
                if "reply" in updates and updates["reply"]:
                    notify(owner, "message_reply", "作者回复了你的留言：" + str(updates["reply"])[:30], "/message")
                elif updates.get("is_public"):
                    notify(owner, "message_public", "你的留言被公开了", "/message")
        except Exception as ne:
            print("通知留言失败:", ne)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/messages/delete", methods=["POST"])
def api_admin_messages_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    token = data.get("token", "")
    msg_id = data.get("id")
    if not token or not msg_id:
        return jsonify({"error": "缺少参数"}), 400
    try:
        resp = supabase.auth.get_user(token)
        if resp.user.email != ADMIN_EMAIL:
            return jsonify({"error": "无权限"}), 403
        supabase.table("messages").delete().eq("id", msg_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/register", methods=["POST"])
def api_register():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "邮箱和密码不能为空"}), 400
    try:
        resp = supabase.auth.sign_up({"email": email, "password": password})
        return jsonify({"success": True, "email": resp.user.email})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/login", methods=["POST"])
def api_login():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    try:
        resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return jsonify({"success": True, "access_token": resp.session.access_token, "email": resp.user.email})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/me", methods=["POST"])
def api_me():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    token = data.get("token", "")
    try:
        resp = supabase.auth.get_user(token)
        return jsonify({"email": resp.user.email})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/api/google_login", methods=["POST"])
def api_google_login():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        data = request.get_json() or {}
        back = data.get("back", "/") or "/"
        if not back.startswith("/"):
            back = "/"
        redirect = "https://student-hub-spain.onrender.com/login?back=" + back
        resp = supabase.auth.sign_in_with_oauth({"provider": "google", "options": {"redirect_to": redirect}})
        return jsonify({"url": resp.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/exchange_code", methods=["POST"])
def api_exchange_code():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "缺少 code"}), 400
    try:
        resp = supabase.auth.exchange_code_for_session({"auth_code": code})
        print("换码成功:", resp.user.email)
        return jsonify({"access_token": resp.session.access_token, "email": resp.user.email})
    except Exception as e:
        print("换码失败:", str(e))
        return jsonify({"error": str(e)}), 400

@app.route("/api/check_admin", methods=["POST"])
def api_check_admin():
    data = request.get_json()
    token = data.get("token", "")
    if not token or not supabase:
        return jsonify({"is_admin": False}), 401
    try:
        resp = supabase.auth.get_user(token)
        if resp.user.email == ADMIN_EMAIL:
            return jsonify({"is_admin": True, "email": resp.user.email})
        else:
            return jsonify({"is_admin": False}), 403
    except Exception as e:
        return jsonify({"is_admin": False, "error": str(e)}), 401

@app.route("/api/admin/login_logs", methods=["POST"])
def api_admin_login_logs():
    data = request.get_json()
    token = data.get("token", "")
    if not token or not supabase:
        return jsonify({"error": "未授权"}), 401
    try:
        resp = supabase.auth.get_user(token)
        if resp.user.email != ADMIN_EMAIL:
            return jsonify({"error": "无权限"}), 403
        logs = supabase.table("login_logs").select("*").order("login_time", desc=True).limit(100).execute()
        return jsonify(logs.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dishes")
def api_dishes():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    try:
        if owner:
            result = supabase.table("dishes").select("*").eq("user_email", owner).order("created_at", desc=True).execute()
        else:
            result = supabase.table("dishes").select("*").order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dishes/add", methods=["POST"])
def api_dishes_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    name = data.get("name", "").strip()
    note = data.get("note", "").strip()
    category = data.get("category", "").strip()
    image_url = data.get("image_url", "").strip()
    if not name:
        return jsonify({"error": "菜名不能为空"}), 400
    try:
        supabase.table("dishes").insert({"user_email": email, "name": name, "note": note, "category": category, "image_url": image_url}).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dishes/delete", methods=["POST"])
def api_dishes_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    dish_id = data.get("id")
    if not dish_id:
        return jsonify({"error": "缺少 id"}), 400
    try:
        supabase.table("dishes").delete().eq("id", dish_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/orders")
def api_orders():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    try:
        if owner:
            result = supabase.table("orders").select("*").eq("user_email", owner).order("created_at", desc=True).limit(50).execute()
        else:
            result = supabase.table("orders").select("*").order("created_at", desc=True).limit(50).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/orders/add", methods=["POST"])
def api_orders_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    dish_names = data.get("dishes", [])
    if not dish_names:
        return jsonify({"error": "购物车为空"}), 400
    try:
        supabase.table("orders").insert({"user_email": email, "dishes": json.dumps(dish_names, ensure_ascii=False)}).execute()
        notify(email, "menu_order", "有人点单了！共 " + str(len(dish_names)) + " 道菜", "/menu")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/countdowns")
def api_countdowns():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    try:
        if owner:
            result = supabase.table("countdowns").select("*").eq("user_email", owner).order("event_date", desc=False).execute()
        else:
            result = supabase.table("countdowns").select("*").order("event_date", desc=False).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/countdowns/add", methods=["POST"])
def api_countdowns_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    name = data.get("event_name", "").strip()
    date = data.get("event_date", "").strip()
    if not name or not date:
        return jsonify({"error": "名称和日期不能为空"}), 400
    try:
        supabase.table("countdowns").insert({"user_email": email, "event_name": name, "event_date": date}).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/countdowns/delete", methods=["POST"])
def api_countdowns_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    item_id = data.get("id")
    if not item_id:
        return jsonify({"error": "缺少 id"}), 400
    try:
        supabase.table("countdowns").delete().eq("id", item_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/emergency")
def api_emergency_get():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        result = supabase.table("emergency_cards").select("*").eq("user_email", owner).execute()
        return jsonify(result.data[0] if result.data else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/emergency/save", methods=["POST"])
def api_emergency_save():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少用户"}), 400
    payload = {"user_email": email, "full_name": data.get("full_name", ""), "phone": data.get("phone", ""), "passport": data.get("passport", ""), "nie": data.get("nie", ""), "emergency_contact_name": data.get("emergency_contact_name", ""), "emergency_contact_phone": data.get("emergency_contact_phone", ""), "notes": data.get("notes", ""), "face_id_protected": bool(data.get("face_id_protected", False))}
    try:
        exist = supabase.table("emergency_cards").select("id").eq("user_email", email).execute()
        if exist.data:
            supabase.table("emergency_cards").update(payload).eq("user_email", email).execute()
        else:
            supabase.table("emergency_cards").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/emergency/delete", methods=["POST"])
def api_emergency_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少用户"}), 400
    try:
        supabase.table("emergency_cards").delete().eq("user_email", email).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/letters")
def api_letters():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        result = supabase.table("homesick_letters").select("*").eq("user_email", owner).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/letters/add", methods=["POST"])
def api_letters_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    recipient = data.get("recipient", "").strip()
    content = data.get("content", "").strip()
    deliver_at = data.get("deliver_at") or None
    if not email or not content:
        return jsonify({"error": "缺少内容"}), 400
    try:
        supabase.table("homesick_letters").insert({"user_email": email, "recipient": recipient, "content": content, "deliver_at": deliver_at}).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/letters/due")
def api_letters_due():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    today = date.today().isoformat()
    try:
        result = supabase.table("homesick_letters").select("*").eq("user_email", owner).eq("is_delivered", False).lte("deliver_at", today).not_.is_("deliver_at", "null").execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/letters/read", methods=["POST"])
def api_letters_read():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    letter_id = data.get("id")
    if not letter_id:
        return jsonify({"error": "缺少 id"}), 400
    try:
        supabase.table("homesick_letters").update({"is_delivered": True, "read_at": datetime.now(timezone.utc).isoformat()}).eq("id", letter_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/treeholes")
def api_treeholes():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("treeholes").select("*").order("created_at", desc=True).limit(100).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/treeholes/add", methods=["POST"])
def api_treeholes_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip() or "anonymous"
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "内容不能为空"}), 400
    try:
        supabase.table("treeholes").insert({"user_email": email, "content": content}).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/treeholes/replies")
def api_treeholes_replies():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    tid = request.args.get("id", "").strip()
    if not tid:
        return jsonify({"error": "缺少 id"}), 400
    try:
        result = supabase.table("treehole_replies").select("*").eq("treehole_id", tid).order("created_at", desc=False).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/treeholes/reply", methods=["POST"])
def api_treeholes_reply():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    tid = data.get("treehole_id")
    email = data.get("email", "").strip() or "anonymous"
    content = data.get("content", "").strip()
    if not tid or not content:
        return jsonify({"error": "缺少内容"}), 400
    try:
        supabase.table("treehole_replies").insert({"treehole_id": tid, "user_email": email, "content": content}).execute()
        tree = supabase.table("treeholes").select("user_email").eq("id", tid).execute()
        if tree.data:
            owner = tree.data[0]["user_email"]
            if owner and owner != email and owner != "anonymous":
                notify(owner, "treehole_reply", "有人回复了你的树洞：" + content[:30], "/treehole")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/my_replies")
def api_my_replies():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        my_trees = supabase.table("treeholes").select("id, content").eq("user_email", owner).execute()
        if not my_trees.data:
            return jsonify([])
        tree_ids = [t["id"] for t in my_trees.data]
        tree_map = {t["id"]: t["content"] for t in my_trees.data}
        replies = supabase.table("treehole_replies").select("*").in_("treehole_id", tree_ids).order("created_at", desc=True).limit(50).execute()
        result = []
        for r in replies.data:
            if r.get("user_email") == owner:
                continue
            result.append({"id": r["id"], "treehole_id": r["treehole_id"], "content": r["content"], "created_at": r["created_at"], "tree_content": tree_map.get(r["treehole_id"], "")})
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
#                        桌面布局
# ==========================================================
@app.route("/api/layout")
def api_layout_get():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        result = supabase.table("user_layouts").select("*").eq("user_email", owner).execute()
        if result.data:
            return jsonify({"layout": result.data[0].get("layout")})
        return jsonify({"layout": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/layout/save", methods=["POST"])
def api_layout_save():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    owner = data.get("owner", "").strip()
    layout = data.get("layout", [])
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        exist = supabase.table("user_layouts").select("id").eq("user_email", owner).execute()
        if exist.data:
            supabase.table("user_layouts").update({
                "layout": layout,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("user_email", owner).execute()
        else:
            supabase.table("user_layouts").insert({
                "user_email": owner,
                "layout": layout,
            }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================================
#                        二手市场
# ==========================================================
@app.route("/api/market")
def api_market_list():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("market_items").select("*").order("created_at", desc=True).limit(200).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/add", methods=["POST"])
def api_market_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    title = data.get("title", "").strip()
    if not email or not title:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("market_items").insert({
            "user_email": email,
            "title": title,
            "description": data.get("description", ""),
            "price": data.get("price", ""),
            "contact": data.get("contact", ""),
            "image_url": data.get("image_url", ""),
            "category": data.get("category", ""),
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/delete", methods=["POST"])
def api_market_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    item_id = data.get("id")
    email = data.get("email", "").strip()
    if not item_id or not email:
        return jsonify({"error": "缺少参数"}), 400
    try:
        # 只能删自己的
        supabase.table("market_items").delete().eq("id", item_id).eq("user_email", email).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/view", methods=["POST"])
def api_market_view():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    item_id = data.get("id")
    if not item_id:
        return jsonify({"error": "缺少 id"}), 400
    try:
        cur = supabase.table("market_items").select("views").eq("id", item_id).execute()
        v = (cur.data[0]["views"] if cur.data else 0) or 0
        supabase.table("market_items").update({"views": v + 1}).eq("id", item_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
#                        社区
# ==========================================================
@app.route("/api/community/posts")
def api_community_posts():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("community_posts").select("*").order("created_at", desc=True).limit(200).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/add", methods=["POST"])
def api_community_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    if not email or not title or not content:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("community_posts").insert({
            "user_email": email,
            "title": title,
            "content": content,
            "category": data.get("category", "其他"),
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/replies")
def api_community_replies():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    pid = request.args.get("post_id", "").strip()
    if not pid:
        return jsonify({"error": "缺少 post_id"}), 400
    try:
        result = supabase.table("community_replies").select("*").eq("post_id", pid).order("created_at", desc=False).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/reply", methods=["POST"])
def api_community_reply():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    pid = data.get("post_id")
    email = data.get("email", "").strip()
    content = data.get("content", "").strip()
    if not pid or not email or not content:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("community_replies").insert({
            "post_id": pid,
            "user_email": email,
            "content": content,
        }).execute()
        # 回复数 +1
        cur = supabase.table("community_posts").select("replies_count").eq("id", pid).execute()
        c = (cur.data[0]["replies_count"] if cur.data else 0) or 0
        supabase.table("community_posts").update({"replies_count": c + 1}).eq("id", pid).execute()
        # 通知楼主
        post = supabase.table("community_posts").select("user_email, title").eq("id", pid).execute()
        if post.data:
            owner = post.data[0]["user_email"]
            if owner and owner != email:
                notify(owner, "community_reply", "有人回复了你的帖子：" + content[:30], "/community")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
#                        用户资料
# ==========================================================
@app.route("/api/profile")
def api_profile_get():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("user_profiles").select("*").eq("user_email", email).execute()
        return jsonify(result.data[0] if result.data else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile/save", methods=["POST"])
def api_profile_save():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    payload = {
        "user_email": email,
        "nickname": data.get("nickname", ""),
        "avatar": data.get("avatar", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        exist = supabase.table("user_profiles").select("id").eq("user_email", email).execute()
        if exist.data:
            supabase.table("user_profiles").update(payload).eq("user_email", email).execute()
        else:
            supabase.table("user_profiles").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ==========================================================
#                        汇率
# ==========================================================
@app.route("/api/rates")
def api_rates():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("rates_cache").select("*").order("updated_at", desc=True).limit(1).execute()
        if result.data:
            row = result.data[0]
            return jsonify({
                "EUR_TO_CNY": row.get("eur_to_cny", 7.85),
                "EUR_TO_USD": row.get("eur_to_usd", 1.08),
                "updated_at": row.get("updated_at", ""),
            })
    except Exception as e:
        print("读汇率缓存失败:", e)
    return jsonify({"EUR_TO_CNY": 7.85, "EUR_TO_USD": 1.08, "updated_at": "默认汇率"})


# ==========================================================
#                        记账
# ==========================================================
@app.route("/api/transactions")
def api_transactions():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    try:
        q = supabase.table("transactions").select("*").eq("user_email", owner)
        if start:
            q = q.gte("tx_date", start)
        if end:
            q = q.lte("tx_date", end)
        result = q.order("tx_date", desc=True).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/transactions/add", methods=["POST"])
def api_transactions_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip() or "anonymous"
    ttype = data.get("type", "expense")
    category = data.get("category", "").strip() or "其他"
    amount = data.get("amount", 0)
    currency = data.get("currency", "EUR").strip().upper()
    note = data.get("note", "").strip()
    tx_date = data.get("tx_date", "")
    if not amount or float(amount) <= 0:
        return jsonify({"error": "金额无效"}), 400
    if currency not in ("EUR", "CNY", "USD"):
        return jsonify({"error": "币种无效"}), 400
    try:
        supabase.table("transactions").insert({
            "user_email": email,
            "type": ttype,
            "category": category,
            "amount": float(amount),
            "currency": currency,
            "note": note,
            "tx_date": tx_date,
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/transactions/delete", methods=["POST"])
def api_transactions_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    tx_id = data.get("id")
    if not tx_id:
        return jsonify({"error": "缺少 id"}), 400
    try:
        supabase.table("transactions").delete().eq("id", tx_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
#                 汇率定时抓取（可选，手动调用）
# ==========================================================
@app.route("/api/rates/refresh", methods=["POST"])
def api_rates_refresh():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    import urllib.request
    try:
        req = urllib.request.Request(
            "https://api.frankfurter.app/latest?from=EUR&to=CNY,USD",
            headers={"User-Agent": "trans-spain-tools"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            import json as _json
            payload = _json.loads(r.read().decode("utf-8"))
        cny = payload["rates"]["CNY"]
        usd = payload["rates"]["USD"]
        supabase.table("rates_cache").insert({
            "eur_to_cny": cny,
            "eur_to_usd": usd,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return jsonify({"success": True, "EUR_TO_CNY": cny, "EUR_TO_USD": usd})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)