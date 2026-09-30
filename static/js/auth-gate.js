// 未登录拦截：显示遮罩，用户点按钮才跳登录
(function () {
  const token = localStorage.getItem('access_token');
  if (token) return;

  // 从 <title> 或页面里判断显示什么提示
  const pageTitle = document.title.split('·')[0].trim() || '此功能';

  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed; inset: 0;
    background: rgba(15,12,41,0.98);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 40px 24px; text-align: center;
    z-index: 9999;
  `;
  overlay.innerHTML = `
    <div style="font-size: 56px; margin-bottom: 20px;">🔒</div>
    <div style="font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 10px;">需要登录</div>
    <div style="font-size: 14px; color: #888; line-height: 1.7; margin-bottom: 32px; max-width: 280px;">
      ${pageTitle}需要登录后才能使用。<br>请先登录，再回来吧。
    </div>
    <button id="__goLoginBtn" style="
      width: 100%; max-width: 280px;
      padding: 16px 24px; border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.2);
      background: rgba(160,216,179,0.15); color: #a0d8b3;
      font-size: 16px; font-weight: 700;
      cursor: pointer; margin-bottom: 12px;
      font-family: inherit;
    ">去登录</button>
    <button id="__goHomeBtn" style="
      width: 100%; max-width: 280px;
      padding: 16px 24px; border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.1);
      background: transparent; color: #ccc;
      font-size: 15px; font-weight: 600;
      cursor: pointer;
      font-family: inherit;
    ">回主页</button>
  `;
  document.body.appendChild(overlay);

  document.getElementById('__goLoginBtn').onclick = () => {
    if (navigator.vibrate) navigator.vibrate(10);
    const back = encodeURIComponent(window.location.pathname + window.location.search);
    // 用 replace：不在历史里留被拦页
    location.replace('/login?back=' + back);
  };
  document.getElementById('__goHomeBtn').onclick = () => {
    if (navigator.vibrate) navigator.vibrate(10);
    location.href = '/';
  };
})();