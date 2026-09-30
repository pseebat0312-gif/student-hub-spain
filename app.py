import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz
import calendar
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
        supabase.auth.update_user({"password": password}, jwt=token)
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