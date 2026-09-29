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
    print("⚠️ 环境变量未设置")

ADMIN_EMAIL = "pseebat0312@gmail.com"


# ===== 页面路由 =====
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

    return render_template(
        "home.html",
        spain_time=now_spain.strftime("%Y-%m-%d %H:%M:%S"),
        china_time=now_china.strftime("%Y-%m-%d %H:%M:%S"),
        day_of_year=day_of_year,
        days_left=days_left,
        progress=progress,
        year=year
    )


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


@app.route("/api/reset_password", methods=["POST"])
def api_reset_password():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少邮箱"}), 400
    try:
        supabase.auth.reset_password_email(email)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# ===== 留言板 =====
@app.route("/api/messages")
def api_messages():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("messages").select("*").eq("is_public", True).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/messages/add", methods=["POST"])
def api_messages_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        data = request.get_json()
        email = data.get("email", "").strip()
        content = data.get("content", "").strip()
        if not email or not content:
            return jsonify({"error": "缺少内容"}), 400
        supabase.table("messages").insert({
            "user_email": email,
            "content": content,
            "is_public": False
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 邮箱注册 =====
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


# ===== 邮箱登录 =====
@app.route("/api/login", methods=["POST"])
def api_login():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    try:
        resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return jsonify({
            "success": True,
            "access_token": resp.session.access_token,
            "email": resp.user.email
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===== 获取当前登录用户 =====
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


# ===== Google OAuth 登录 =====
@app.route("/api/google_login", methods=["POST"])
def api_google_login():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        resp = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "https://student-hub-spain.onrender.com/login"
            }
        })
        return jsonify({"url": resp.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ===== 用 OAuth code 换 session =====
@app.route("/api/exchange_code", methods=["POST"])
def api_exchange_code():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "缺少 code"}), 400
    try:
        # Supabase 支持直接用 OAuth code 换 session
        resp = supabase.auth.exchange_code_for_session({"auth_code": code})
        return jsonify({
            "access_token": resp.session.access_token,
            "email": resp.user.email
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ===== 管理员：检查身份 =====
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


# ===== 管理员：所有登录记录 =====
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)