# student-hub-spain
# 🇪🇸 西班牙留学生工具站

> 一个为在西班牙的中国留学生打造的一站式工具站。
> 不用下载 App，加到手机桌面就能像 App 一样使用。

---

## 📖 项目简介

西班牙留学生工具站是一个 **PWA（渐进式 Web 应用）**，集成了 15+ 个实用模块，
覆盖留学生活的方方面面：从汇率换算、记账、二手市场，到论文 AI 检测、急救卡、
共享菜单、匿名树洞、想家急救包等。

项目使用 **Flask + Supabase** 构建，部署在 **Render** 上，完全免费。

---

## ✨ 功能模块

### 🧰 工具类
| 模块 | 功能 |
|------|------|
| ⏳ 倒数日 | 记录回国、考试、签证到期等重要日子 |
| 💱 汇率换算与记账 | 实时欧元/人民币汇率 + 收支记录 |
| 🗺️ 探店地图 | 留学生推荐/避雷的餐厅、奶茶、超市，支持评论和 Google Maps 导航 |
| 🏫 学校导览 | 西班牙主要大学信息 |
| 📋 办事导览 | 办居留、办银行卡、办手机卡等流程 |
| 📰 每日更新 | 每天凌晨自动抓取西班牙新闻，AI 生成中文摘要 |

### 💬 社交类
| 模块 | 功能 |
|------|------|
| ✍️ 留言板 | 给站长留言，可公开 |
| 💬 互助社区 | 发帖、回帖，留学生互助 |
| 🌳 匿名树洞 | 匿名发帖，支持回复 |
| 🛒 二手市场 | 发布/浏览二手物品，带浏览量统计 |
| 🍽️ 独家菜单 | 和室友共享菜单，支持导出精美菜单图 |

### 🏠 情感与安全类
| 模块 | 功能 |
|------|------|
| 🏠 想家急救包 | 写一封定时寄出的家书，到期自动出现 |
| 🆘 急救卡 | 护照、NIE、紧急联系人，离线也能看 |
| 🎀 Girl's Room | 经期记录、追星心肝、遇险暗号、位置共享 |

### 👑 会员系统
- **免费用户**：每个 AI 功能试用 3 次
- **VIP 会员**：无限使用所有功能
- **激活方式**：
  - 🎫 兑换码（测试阶段）
  - 💳 Stripe 订阅（开发中，首月 €1）

---

## 🛠️ 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3 + Flask |
| 数据库 | Supabase (PostgreSQL) |
| 认证 | Supabase Auth |
| 文件存储 | Supabase Storage |
| AI | DeepSeek API |
| 地图 | Leaflet + OpenStreetMap |
| 新闻抓取 | feedparser + RSS |
| 前端 | 原生 HTML / CSS / JS，PWA |
| 部署 | Render (免费版) |

---

## 📁 项目结构
student-hub-spain/
  app.py                      Flask 主应用，所有路由和 API
  requirements.txt            Python 依赖
  daily_update.py             每日新闻抓取脚本（定时任务）
  templates/                  HTML 页面
    home.html                 主页（PWA 外壳 + 应用网格）
    login.html                登录/注册
    profile.html              个人中心
    vip.html                  VIP 会员页
    menu.html                 独家菜单
    map.html                  探店地图
    community.html            互助社区
    market.html               二手市场
    treehole.html             匿名树洞
    message.html              留言板
    countdown.html            倒数日
    currency.html             汇率+记账
    emergency.html            急救卡
    homesick.html             想家急救包
    her.html                  Girl's Room
    travel.html               足迹地图
  static/
    style.css                 全局样式
    js/
      auth-gate.js            登录态检查
      vip-gate.js             VIP 试用/锁定/引导
  README.md

---

## 本地运行

### 1. 克隆项目

git clone https://github.com/your-username/student-hub-spain.git
cd student-hub-spain

### 2. 安装依赖

pip install -r requirements.txt

requirements.txt 内容：

Flask
supabase
pytz
feedparser
openai

### 3. 配置环境变量

在项目根目录创建 .env 或直接设置系统环境变量：

SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
DEEPSEEK_API_KEY=your-deepseek-key

### 4. 初始化数据库

在 Supabase SQL Editor 里执行项目中的建表脚本。
主要表：

- user_profiles — 用户资料 + VIP 状态
- ai_usage — AI 功能使用记录
- vip_codes — 兑换码
- dishes / orders — 菜单
- menu_shares — 菜单共享关系
- shops / shop_comments — 探店地图
- community_posts / community_replies — 社区
- market_items — 二手市场
- treeholes / treehole_replies — 树洞
- messages — 留言板
- notifications — 通知
- daily_digest — 每日新闻
- her_* — Girl's Room 相关
- user_travel / location_shares / user_locations — 足迹 + 位置共享

### 5. 启动

python app.py

访问 http://localhost:5000

---

## 部署到 Render

### 1. 创建 Web Service

- 关联 GitHub 仓库
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app

### 2. 配置环境变量

在 Render Dashboard → Environment 里加：

SUPABASE_URL=...
SUPABASE_KEY=...
DEEPSEEK_API_KEY=...

### 3. 定时任务（每日新闻）

在 Render → New → Cron Job：

- Command: python daily_update.py
- Schedule: 0 3 * * *  （每天凌晨 3 点）

### 4. 自定义域名（可选）

- Render → Settings → Custom Domain
- 添加你的域名，按提示改 DNS
- 证书由 Render 自动管理，免费且自动续期

---

## 安全与认证

- 用户认证：Supabase Auth（邮箱 + 密码 / Google OAuth）
- 文件上传：Supabase Storage（avatars / market 两个 bucket）
- 权限校验：管理员接口用 supabase.auth.get_user(token) 校验邮箱
- VIP 判断：通过 user_profiles.is_vip + vip_expire_at 双重校验
- RLS：当前所有表已关闭 RLS，由后端统一管控（开发阶段）

注意：当前所有写接口通过前端传 email 参数识别用户，
这属于开发阶段的简化方案。未来若对外开放，建议改为基于 token 的服务端鉴权。

---

## PWA 支持

- 支持「添加到手机桌面」
- 全屏无浏览器边框
- 独立图标
- 离线访问基础页面

iOS 添加方法：Safari → 分享 → 添加到主屏幕
Android 添加方法：Chrome → 菜单 → 添加到主屏幕

---

## VIP 系统

### 免费限制

- AI 检测：3 次
- 菜单添加：8 道菜
- 导出菜单：VIP 专属

### 兑换码（测试阶段）

在 Supabase 里插入：

insert into vip_codes (code) values ('SPAIN01'), ('SPAIN02'), ...;

用户在 /vip 页面输入即可激活 30 天 VIP。

### Stripe 订阅（开发中）

- 首月 1 欧，之后 2.99 欧/月
- 自动续费
- 用户可在 Stripe Customer Portal 自行取消

---

## 贡献

这是一个个人项目，欢迎提 Issue 或 PR。
如果你是在西班牙的留学生，想一起完善它，欢迎联系。

---

## License

MIT

---

## 致谢

感谢所有在西班牙努力生活的留学生。
希望这个小工具站，能让你的留学生活轻松一点点。