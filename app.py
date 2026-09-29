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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)