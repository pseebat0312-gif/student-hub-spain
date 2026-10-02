import os
import json
from datetime import datetime, date, timedelta, timezone
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

@app.route("/vip")
def vip_page():
    return render_template("vip.html")

@app.route("/travel")
def travel():
    return render_template("travel.html")

@app.route("/her")
def her():
    return render_template("her.html")






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

# ==========================================================
#                        菜单共享
# ==========================================================
@app.route("/api/menu/shares")
def api_menu_shares():
    """返回当前用户所在的共享组的所有成员邮箱"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        # 我发起的 + 别人发给我的
        sent = supabase.table("menu_shares").select("member_email").eq("owner_email", email).execute()
        received = supabase.table("menu_shares").select("owner_email").eq("member_email", email).execute()
        group = set()
        group.add(email)
        for r in (sent.data or []):
            group.add(r["member_email"])
        for r in (received.data or []):
            group.add(r["owner_email"])
        members = sorted(list(group))
        # 组的 owner = 排序后第一个
        owner = members[0] if members else email
        return jsonify({"members": members, "owner": owner})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/menu/share/add", methods=["POST"])
def api_menu_share_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    owner = data.get("owner", "").strip().lower()
    member = data.get("member", "").strip().lower()
    if not owner or not member:
        return jsonify({"error": "缺少参数"}), 400
    if owner == member:
        return jsonify({"error": "不能和自己共享"}), 400
    try:
        exist = supabase.table("menu_shares").select("id").eq("owner_email", owner).eq("member_email", member).execute()
        if exist.data:
            return jsonify({"error": "已经共享过了"}), 400
        supabase.table("menu_shares").insert({
            "owner_email": owner,
            "member_email": member
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/menu/share/remove", methods=["POST"])
def api_menu_share_remove():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    owner = data.get("owner", "").strip().lower()
    member = data.get("member", "").strip().lower()
    if not owner or not member:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("menu_shares").delete().eq("owner_email", owner).eq("member_email", member).execute()
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
#                        每日更新
# ==========================================================
@app.route("/api/digest")
def api_digest():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    try:
        result = (
            supabase.table("daily_digest")
            .select("*")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return jsonify(result.data or [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/digest")
def digest_page():
    return render_template("digest.html")


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
        cur = supabase.table("community_posts").select("replies_count").eq("id", pid).execute()
        c = (cur.data[0]["replies_count"] if cur.data else 0) or 0
        supabase.table("community_posts").update({"replies_count": c + 1}).eq("id", pid).execute()
        post = supabase.table("community_posts").select("user_email, title").eq("id", pid).execute()
        if post.data:
            owner = post.data[0]["user_email"]
            if owner and owner != email:
                notify(owner, "community_reply", "有人回复了你的帖子：" + content[:30], "/community")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/community/delete", methods=["POST"])
def api_community_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    post_id = data.get("id")
    email = data.get("email", "").strip()
    if not post_id or not email:
        return jsonify({"error": "缺少参数"}), 400
    try:
        # 只能删自己的
        supabase.table("community_posts").delete().eq("id", post_id).eq("user_email", email).execute()
        # 顺便删掉这个帖子下的所有回复
        supabase.table("community_replies").delete().eq("post_id", post_id).execute()
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
        result = supabase.table("user_profiles").select("*").eq("email", email).execute()
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
    nickname = data.get("nickname", "")
    avatar_url = data.get("avatar_url", "")
    avatar_emoji = data.get("avatar_emoji", "")
    payload = {
        "email": email,
        "nickname": nickname,
        "avatar_url": avatar_url,
        "avatar_emoji": avatar_emoji,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        exist = supabase.table("user_profiles").select("email").eq("email", email).execute()
        if exist.data:
            supabase.table("user_profiles").update(payload).eq("email", email).execute()
        else:
            supabase.table("user_profiles").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from werkzeug.utils import secure_filename
import uuid



# ==========================================================
#                        VIP 系统
# ==========================================================
FREE_LIMIT = 3   # 免费用户每个功能试用 2 次

VIP_FEATURES = {
    "ai_detect": "AI 检测",
    "resume": "AI 简历",
    "contract": "合同扫描",
    "culture_calendar": "文化日历",
    "nearby": "附近网点",
    "price_compare": "超市比价",
}


@app.route("/api/vip/status")
def api_vip_status():
    """查询当前用户是否是 VIP"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("user_profiles").select("is_vip,vip_expire_at").eq("email", email).execute()
        if not result.data:
            return jsonify({"is_vip": False, "expire_at": None})
        row = result.data[0]
        is_vip = bool(row.get("is_vip"))
        expire_at = row.get("vip_expire_at")
        # 过期检查
        if is_vip and expire_at:
            from datetime import datetime as _dt
            exp = _dt.fromisoformat(expire_at.replace("Z", "+00:00"))
            if exp < _dt.now(timezone.utc):
                is_vip = False
        return jsonify({"is_vip": is_vip, "expire_at": expire_at})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vip/check_usage")
def api_vip_check_usage():
    """检查某功能剩余免费次数"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip().lower()
    feature = request.args.get("feature", "").strip()
    if not email or not feature:
        return jsonify({"error": "缺少参数"}), 400
    try:
        # 先查 VIP
        prof = supabase.table("user_profiles").select("is_vip,vip_expire_at").eq("email", email).execute()
        is_vip = False
        if prof.data:
            is_vip = bool(prof.data[0].get("is_vip"))
            exp = prof.data[0].get("vip_expire_at")
            if is_vip and exp:
                from datetime import datetime as _dt
                e = _dt.fromisoformat(exp.replace("Z", "+00:00"))
                if e < _dt.now(timezone.utc):
                    is_vip = False
        if is_vip:
            return jsonify({"is_vip": True, "remaining": -1})   # -1 = 无限

        # 查免费次数
        used = supabase.table("ai_usage").select("id", count="exact").eq("user_email", email).eq("feature", feature).execute()
        used_count = used.count if hasattr(used, "count") and used.count is not None else len(used.data or [])
        remaining = max(0, FREE_LIMIT - used_count)
        return jsonify({"is_vip": False, "remaining": remaining, "limit": FREE_LIMIT})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vip/consume", methods=["POST"])
def api_vip_consume():
    """消耗一次免费次数（或 VIP 无限制直接返回 ok）"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    feature = data.get("feature", "").strip()
    if not email or not feature:
        return jsonify({"error": "缺少参数"}), 400
    try:
        # VIP 直接放行
        prof = supabase.table("user_profiles").select("is_vip,vip_expire_at").eq("email", email).execute()
        if prof.data and prof.data[0].get("is_vip"):
            exp = prof.data[0].get("vip_expire_at")
            if exp:
                from datetime import datetime as _dt
                e = _dt.fromisoformat(exp.replace("Z", "+00:00"))
                if e >= _dt.now(timezone.utc):
                    return jsonify({"success": True, "is_vip": True})
            else:
                return jsonify({"success": True, "is_vip": True})

        # 免费用户：检查剩余
        used = supabase.table("ai_usage").select("id", count="exact").eq("user_email", email).eq("feature", feature).execute()
        used_count = used.count if hasattr(used, "count") and used.count is not None else len(used.data or [])
        if used_count >= FREE_LIMIT:
            return jsonify({"error": "免费次数已用完", "need_vip": True}), 403

        # 记一次
        supabase.table("ai_usage").insert({
            "user_email": email,
            "feature": feature
        }).execute()
        return jsonify({"success": True, "is_vip": False, "remaining": FREE_LIMIT - used_count - 1})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vip/redeem", methods=["POST"])
def api_vip_redeem():
    """兑换码激活 VIP（Stripe 激活前的临时方案）"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip().upper()
    if not email or not code:
        return jsonify({"error": "缺少参数"}), 400
    try:
        # 查兑换码
        r = supabase.table("vip_codes").select("*").eq("code", code).execute()
        if not r.data:
            return jsonify({"error": "兑换码无效"}), 400
        row = r.data[0]
        if row.get("used_by"):
            return jsonify({"error": "兑换码已被使用"}), 400

        # 激活 VIP（30 天）
        from datetime import datetime as _dt
        now = _dt.now(timezone.utc)
        expire = now + timedelta(days=30)

        payload = {
            "is_vip": True,
            "vip_expire_at": expire.isoformat(),
            "updated_at": now.isoformat()
        }
        exist = supabase.table("user_profiles").select("email").eq("email", email).execute()
        if exist.data:
            supabase.table("user_profiles").update(payload).eq("email", email).execute()
        else:
            supabase.table("user_profiles").insert({"email": email, **payload}).execute()

        # 标记兑换码已用
        supabase.table("vip_codes").update({
            "used_by": email,
            "used_at": now.isoformat()
        }).eq("code", code).execute()

        return jsonify({"success": True, "expire_at": expire.isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
#            Stripe Webhook（激活后接）
# ==========================================================
@app.route("/api/stripe/webhook", methods=["POST"])
def api_stripe_webhook():
    """
    Stripe 付款成功后回调
    需要环境变量 STRIPE_WEBHOOK_SECRET
    在 Stripe Dashboard → Developers → Webhooks 配置
    事件：checkout.session.completed
    """
    import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email", "").lower()
        subscription_id = session.get("subscription")

        if customer_email and supabase:
            try:
                from datetime import datetime as _dt
                now = _dt.now(timezone.utc)
                expire = now + timedelta(days=31)

                payload = {
                    "is_vip": True,
                    "vip_expire_at": expire.isoformat(),
                    "stripe_customer_id": session.get("customer", ""),
                    "updated_at": now.isoformat()
                }
                exist = supabase.table("user_profiles").select("email").eq("email", customer_email).execute()
                if exist.data:
                    supabase.table("user_profiles").update(payload).eq("email", customer_email).execute()
                else:
                    supabase.table("user_profiles").insert({"email": customer_email, **payload}).execute()
            except Exception as e:
                print("Stripe webhook 写库失败:", e)

    return jsonify({"received": True}), 200



@app.route("/api/upload", methods=["POST"])
def api_upload():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    bucket = request.form.get("bucket", "avatars")
    if bucket not in ("avatars", "market"):
        return jsonify({"error": "bucket 不合法"}), 400
    if "file" not in request.files:
        return jsonify({"error": "没有文件"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "文件名为空"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "gif", "webp", "heic"):
        return jsonify({"error": "文件类型不支持"}), 400
    # 限 10MB
    f.seek(0, 2)
    size = f.tell()
    f.seek(0)
    if size > 10 * 1024 * 1024:
        return jsonify({"error": "文件太大，最多 10MB"}), 400
    name = f"{uuid.uuid4().hex}.{ext}"
    try:
        content = f.read()
        supabase.storage.from_(bucket).upload(
            name, content, {"content-type": f.mimetype or "image/jpeg"}
        )
        url = supabase.storage.from_(bucket).get_public_url(name)
        return jsonify({"success": True, "url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ==========================================================
#                    Girl's Room · 经期
# ==========================================================
@app.route("/api/her_cycles")
def api_her_cycles_list():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("her_cycles").select("*").eq("user_email", email).order("start_date", desc=False).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_cycles/add", methods=["POST"])
def api_her_cycles_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    start_date = data.get("start_date", "").strip()
    end_date = data.get("end_date", "").strip() or None
    if not email or not start_date:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("her_cycles").insert({
            "user_email": email,
            "start_date": start_date,
            "end_date": end_date,
            "flow": data.get("flow", ""),
            "symptoms": data.get("symptoms", []),
            "note": data.get("note", ""),
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_cycles/delete", methods=["POST"])
def api_her_cycles_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    cycle_id = data.get("id")
    email = data.get("email", "").strip()
    if not cycle_id or not email:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("her_cycles").delete().eq("id", cycle_id).eq("user_email", email).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
#                    Girl's Room · 心肝
# ==========================================================
@app.route("/api/her_idols")
def api_her_idols_list():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("her_idols").select("*").eq("user_email", email).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_idols/add", methods=["POST"])
def api_her_idols_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    group_name = data.get("group_name", "").strip()
    member_name = data.get("member_name", "").strip()
    if not email or not group_name or not member_name:
        return jsonify({"error": "缺少参数"}), 400
    try:
        exist = supabase.table("her_idols").select("id").eq("user_email", email).eq("group_name", group_name).eq("member_name", member_name).execute()
        if exist.data:
            return jsonify({"error": "已经在你的心肝列表里了"}), 400
        supabase.table("her_idols").insert({
            "user_email": email,
            "group_name": group_name,
            "member_name": member_name,
            "nickname": data.get("nickname", ""),
            "avatar_url": data.get("avatar_url", ""),
            "avatar_emoji": data.get("avatar_emoji", ""),
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_idols/update", methods=["POST"])
def api_her_idols_update():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    idol_id = data.get("id")
    email = data.get("email", "").strip()
    if not idol_id or not email:
        return jsonify({"error": "缺少参数"}), 400
    payload = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if "nickname" in data: payload["nickname"] = data["nickname"]
    if "avatar_url" in data: payload["avatar_url"] = data["avatar_url"]
    if "avatar_emoji" in data: payload["avatar_emoji"] = data["avatar_emoji"]
    try:
        supabase.table("her_idols").update(payload).eq("id", idol_id).eq("user_email", email).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_idols/delete", methods=["POST"])
def api_her_idols_delete():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    idol_id = data.get("id")
    email = data.get("email", "").strip()
    if not idol_id or not email:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("her_idols").delete().eq("id", idol_id).eq("user_email", email).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/her_chats")
def api_her_chats_list():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    idol_id = request.args.get("idol_id", "").strip()
    if not email or not idol_id:
        return jsonify({"error": "缺少参数"}), 400
    try:
        result = supabase.table("her_chats").select("*").eq("user_email", email).eq("idol_id", idol_id).order("created_at", desc=False).limit(200).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_chats/add", methods=["POST"])
def api_her_chats_add():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    idol_id = data.get("idol_id")
    content = data.get("content", "").strip()
    if not email or not idol_id or not content:
        return jsonify({"error": "缺少参数"}), 400
    try:
        supabase.table("her_chats").insert({
            "user_email": email,
            "idol_id": idol_id,
            "content": content
        }).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ==========================================================
#                   Girl's Room · 遇险暗号
# ==========================================================
@app.route("/api/her_safety")
def api_her_safety_get():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("her_safety").select("*").eq("user_email", email).execute()
        return jsonify(result.data[0] if result.data else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_safety/save", methods=["POST"])
def api_her_safety_save():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    payload = {
        "user_email": email,
        "secret_code": data.get("secret_code", ""),
        "pin_hash": data.get("pin_hash", ""),
        "contacts": data.get("contacts", []),
        "webauthn_enabled": bool(data.get("webauthn_enabled", False)),
        "webauthn_credential_id": data.get("webauthn_credential_id", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        exist = supabase.table("her_safety").select("id").eq("user_email", email).execute()
        if exist.data:
            supabase.table("her_safety").update(payload).eq("user_email", email).execute()
        else:
            supabase.table("her_safety").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ==========================================================
#               Girl's Room · 暗号共享
# ==========================================================
@app.route("/api/her_safety/shares")
def api_her_safety_shares():
    """返回我发出去的 + 别人发给我的"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        sent = supabase.table("her_safety_shares").select("*").eq("owner_email", email).execute()
        received = supabase.table("her_safety_shares").select("*").eq("viewer_email", email).execute()
        return jsonify({
            "sent": sent.data or [],
            "received": received.data or []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_safety/share/invite", methods=["POST"])
def api_her_safety_share_invite():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    owner = data.get("owner", "").strip().lower()
    viewer = data.get("viewer", "").strip().lower()
    if not owner or not viewer:
        return jsonify({"error": "缺少参数"}), 400
    if owner == viewer:
        return jsonify({"error": "不能共享给自己"}), 400
    try:
        exist = supabase.table("her_safety_shares").select("id,status").eq("owner_email", owner).eq("viewer_email", viewer).execute()
        if exist.data:
            return jsonify({"error": "已经邀请过了"}), 400
        supabase.table("her_safety_shares").insert({
            "owner_email": owner,
            "viewer_email": viewer,
            "status": "pending"
        }).execute()
        try:
            supabase.table("notifications").insert({
                "user_email": viewer,
                "type": "safety_share_invite",
                "content": owner + " 想和你共享遇险暗号",
                "link": "/her"
            }).execute()
        except Exception:
            pass
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_safety/share/respond", methods=["POST"])
def api_her_safety_share_respond():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    share_id = data.get("id")
    action = data.get("action")  # accept / reject / remove
    email = data.get("email", "").strip().lower()
    if not share_id or action not in ("accept", "reject", "remove") or not email:
        return jsonify({"error": "缺少参数"}), 400
    try:
        row = supabase.table("her_safety_shares").select("*").eq("id", share_id).execute()
        if not row.data:
            return jsonify({"error": "记录不存在"}), 404
        r = row.data[0]
        if email not in (r["owner_email"], r["viewer_email"]):
            return jsonify({"error": "无权限"}), 403
        if action == "remove":
            supabase.table("her_safety_shares").delete().eq("id", share_id).execute()
        else:
            new_status = "accepted" if action == "accept" else "rejected"
            supabase.table("her_safety_shares").update({"status": new_status}).eq("id", share_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/her_safety/shared_with_me")
def api_her_safety_shared_with_me():
    """我守护的人（已接受共享的）的暗号+联系人"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        shares = supabase.table("her_safety_shares").select("owner_email").eq("viewer_email", email).eq("status", "accepted").execute()
        owners = [s["owner_email"] for s in (shares.data or [])]
        if not owners:
            return jsonify([])
        safeties = supabase.table("her_safety").select("user_email,secret_code,contacts").in_("user_email", owners).execute()
        return jsonify(safeties.data or [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ==========================================================
#                        足迹地图
# ==========================================================
@app.route("/api/travel")
def api_travel_get():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("user_travel").select("*").eq("user_email", email).execute()
        if result.data:
            return jsonify(result.data[0])
        return jsonify({"visited": [], "wishlist": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/travel/save", methods=["POST"])
def api_travel_save():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    visited = data.get("visited", [])
    wishlist = data.get("wishlist", [])
    if not isinstance(visited, list): visited = []
    if not isinstance(wishlist, list): wishlist = []
    try:
        exist = supabase.table("user_travel").select("id").eq("user_email", email).execute()
        payload = {
            "user_email": email,
            "visited": visited,
            "wishlist": wishlist,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if exist.data:
            supabase.table("user_travel").update(payload).eq("user_email", email).execute()
        else:
            supabase.table("user_travel").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
#                        位置共享
# ==========================================================
@app.route("/api/location/update", methods=["POST"])
def api_location_update():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    lat = data.get("lat")
    lng = data.get("lng")
    if not email or lat is None or lng is None:
        return jsonify({"error": "缺少参数"}), 400
    try:
        payload = {
            "user_email": email,
            "lat": float(lat),
            "lng": float(lng),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        exist = supabase.table("user_locations").select("user_email").eq("user_email", email).execute()
        if exist.data:
            supabase.table("user_locations").update(payload).eq("user_email", email).execute()
        else:
            supabase.table("user_locations").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/location/stop", methods=["POST"])
def api_location_stop():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        supabase.table("user_locations").delete().eq("user_email", email).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/location/friends")
def api_location_friends():
    """返回我的好友列表（我共享给的和共享给我的），带他们的位置"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        # 我发给别人的
        sent = supabase.table("location_shares").select("*").eq("owner_email", email).execute()
        # 别人发给我的
        received = supabase.table("location_shares").select("*").eq("friend_email", email).execute()
        return jsonify({
            "sent": sent.data or [],
            "received": received.data or [],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/location/share", methods=["POST"])
def api_location_share():
    """发起共享邀请"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    owner = data.get("owner", "").strip().lower()
    friend = data.get("friend", "").strip().lower()
    if not owner or not friend:
        return jsonify({"error": "缺少参数"}), 400
    if owner == friend:
        return jsonify({"error": "不能共享给自己"}), 400
    try:
        exist = supabase.table("location_shares").select("id,status").eq("owner_email", owner).eq("friend_email", friend).execute()
        if exist.data:
            return jsonify({"error": "已经邀请过了"}), 400
        supabase.table("location_shares").insert({
            "owner_email": owner,
            "friend_email": friend,
            "status": "pending",
        }).execute()
        # 通知对方
        notify(friend, "location_invite", owner + " 想和你共享位置", "/travel")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/location/respond", methods=["POST"])
def api_location_respond():
    """接受或拒绝共享邀请"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    share_id = data.get("id")
    action = data.get("action")  # accept / reject / remove
    email = data.get("email", "").strip().lower()
    if not share_id or action not in ("accept", "reject", "remove") or not email:
        return jsonify({"error": "缺少参数"}), 400
    try:
        # 校验权限：只能操作跟我有关的
        row = supabase.table("location_shares").select("*").eq("id", share_id).execute()
        if not row.data:
            return jsonify({"error": "记录不存在"}), 404
        r = row.data[0]
        if email not in (r["owner_email"], r["friend_email"]):
            return jsonify({"error": "无权限"}), 403
        if action == "remove":
            supabase.table("location_shares").delete().eq("id", share_id).execute()
        else:
            new_status = "accepted" if action == "accept" else "rejected"
            supabase.table("location_shares").update({"status": new_status}).eq("id", share_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/location/positions")
def api_location_positions():
    """返回我所有已接受好友的实时位置"""
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        # 拿到所有 accepted 的共享关系
        sent = supabase.table("location_shares").select("friend_email").eq("owner_email", email).eq("status", "accepted").execute()
        received = supabase.table("location_shares").select("owner_email").eq("friend_email", email).eq("status", "accepted").execute()
        friend_emails = set()
        for r in (sent.data or []): friend_emails.add(r["friend_email"])
        for r in (received.data or []): friend_emails.add(r["owner_email"])
        friend_emails.discard(email)
        if not friend_emails:
            return jsonify([])
        # 拿这些人的位置
        positions = supabase.table("user_locations").select("*").in_("user_email", list(friend_emails)).execute()
        return jsonify(positions.data or [])
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




# ==========================================================
#                        汇率提醒
# ==========================================================
@app.route("/api/rate_alerts")
def api_rate_alerts_get():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    try:
        result = supabase.table("rate_alerts").select("*").eq("user_email", email).execute()
        if result.data:
            return jsonify(result.data[0])
        return jsonify({
            "user_email": email,
            "enabled": False,
            "upper_threshold": 8.00,
            "lower_threshold": 7.00,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/rate_alerts/save", methods=["POST"])
def api_rate_alerts_save():
    if not supabase:
        return jsonify({"error": "数据库未连接"}), 500
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "缺少 email"}), 400
    payload = {
        "user_email": email,
        "enabled": bool(data.get("enabled", False)),
        "upper_threshold": float(data.get("upper_threshold", 8.00)),
        "lower_threshold": float(data.get("lower_threshold", 7.00)),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        exist = supabase.table("rate_alerts").select("id").eq("user_email", email).execute()
        if exist.data:
            supabase.table("rate_alerts").update(payload).eq("user_email", email).execute()
        else:
            supabase.table("rate_alerts").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
