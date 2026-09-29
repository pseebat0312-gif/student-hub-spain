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



# ===== 重置密码（发邮件） =====
@app.route("/api/reset_password", methods=["POST"])
def api_reset_password():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少邮箱"}), 400
    try:
        supabase.auth.reset_password_email(
            email,
            {"redirect_to": "https://student-hub-spain.onrender.com/reset-password"}
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ===== 用 token 更新密码 =====
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
        supabase.table("messages").insert({
            "user_email": email,
            "content": content,
            "is_public": False
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ===== 管理员：读取所有留言 =====
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


# ===== 管理员：更新留言（回复/公开/取消公开） =====
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
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 管理员：删除留言 =====
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
        resp = supabase.auth.exchange_code_for_session({"auth_code": code})
        print("✅ 换码成功：", resp.user.email)
        return jsonify({
            "access_token": resp.session.access_token,
            "email": resp.user.email
        })
    except Exception as e:
        print("❌ 换码失败：", str(e))
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


# ===== 菜品：读取（按 owner 邮箱） =====
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


# ===== 菜品：添加 =====
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
        supabase.table("dishes").insert({
            "user_email": email,
            "name": name,
            "note": note,
            "category": category,
            "image_url": image_url
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 菜品：删除 =====
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


# ===== 订单：读取（按 owner 邮箱） =====
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


# ===== 订单：保存 =====
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
        import json
        supabase.table("orders").insert({
            "user_email": email,
            "dishes": json.dumps(dish_names, ensure_ascii=False)
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== 倒数日：读取（按 owner 邮箱） =====
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


# ===== 倒数日：添加 =====
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
        supabase.table("countdowns").insert({
            "user_email": email,
            "event_name": name,
            "event_date": date
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 倒数日：删除 =====
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

# ===== 急救卡：读取 =====
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


# ===== 急救卡：保存 =====
@app.route("/api/emergency/save", methods=["POST"])
def api_emergency_save():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少用户"}), 400
    payload = {
        "user_email": email,
        "full_name": data.get("full_name", ""),
        "phone": data.get("phone", ""),
        "passport": data.get("passport", ""),
        "nie": data.get("nie", ""),
        "emergency_contact_name": data.get("emergency_contact_name", ""),
        "emergency_contact_phone": data.get("emergency_contact_phone", ""),
        "notes": data.get("notes", ""),
        "face_id_protected": bool(data.get("face_id_protected", False))
    }
    try:
        exist = supabase.table("emergency_cards").select("id").eq("user_email", email).execute()
        if exist.data:
            supabase.table("emergency_cards").update(payload).eq("user_email", email).execute()
        else:
            supabase.table("emergency_cards").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 急救卡：删除 =====
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

# ===== 想家信：读取我的全部信 =====
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


# ===== 想家信：保存 =====
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
        supabase.table("homesick_letters").insert({
            "user_email": email,
            "recipient": recipient,
            "content": content,
            "deliver_at": deliver_at
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 想家信：检查有没有到期的信 =====
@app.route("/api/letters/due")
def api_letters_due():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    owner = request.args.get("owner", "").strip()
    if not owner:
        return jsonify({"error": "缺少 owner"}), 400
    from datetime import date
    today = date.today().isoformat()
    try:
        result = supabase.table("homesick_letters").select("*")\
            .eq("user_email", owner)\
            .eq("is_delivered", False)\
            .lte("deliver_at", today)\
            .not_.is_("deliver_at", "null")\
            .execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 想家信：标记已读 =====
@app.route("/api/letters/read", methods=["POST"])
def api_letters_read():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    letter_id = data.get("id")
    if not letter_id:
        return jsonify({"error": "缺少 id"}), 400
    from datetime import datetime
    try:
        supabase.table("homesick_letters").update({
            "is_delivered": True,
            "read_at": datetime.utcnow().isoformat()
        }).eq("id", letter_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== 树洞：读取全部 =====
@app.route("/api/treeholes")
def api_treeholes():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = supabase.table("treeholes").select("*").order("created_at", desc=True).limit(100).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 树洞：发布 =====
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
        supabase.table("treeholes").insert({
            "user_email": email,
            "content": content
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== 树洞：读取某条的评论 =====
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


# ===== 树洞：发布评论 =====
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
        supabase.table("treehole_replies").insert({
            "treehole_id": tid,
            "user_email": email,
            "content": content
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)