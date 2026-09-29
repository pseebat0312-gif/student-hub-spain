import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("⚠️ 环境变量未设置")


from flask import Flask, render_template
from datetime import datetime
import pytz
import calendar

app = Flask(__name__)

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


@app.route("/")
def index():
    # 西班牙时间
    spain_tz = pytz.timezone("Europe/Madrid")
    now_spain = datetime.now(spain_tz)
    # 中国时间
    china_tz = pytz.timezone("Asia/Shanghai")
    now_china = datetime.now(china_tz)

    # 今年进度
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


# ===== 留言板：读取公开留言 =====
@app.route("/api/messages")
def api_messages():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("messages").select("*").eq("is_public", True).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 留言板：提交新留言 =====
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


    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)