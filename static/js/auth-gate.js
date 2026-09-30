// 未登录拦截：显示锁屏，提示用户回主页登录
(function () {
  const token = localStorage.getItem('access_token');
  if (token) return;

  const pageTitle = document.title.split('·')[0].trim() || '此功能';

  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed; inset: 0;
    background: rgba(10,8,30,0.98);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 40px 24px; text-align: center;
    z-index: 9999;
    animation: __gateFadeIn 0.3s ease;
  `;
  overlay.innerHTML = `
    <style>
      @keyframes __gateFadeIn { from { opacity: 0; } to { opacity: 1; } }
      @keyframes __gatePulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.06); opacity: 0.85; }
      }
      #__gateCard {
        width: 100%; max-width: 340px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 26px;
        padding: 32px 24px 26px;
        text-align: center;
      }
      #__gateLock {
        font-size: 64px;
        line-height: 1;
        margin-bottom: 18px;
        animation: __gatePulse 2.4s ease-in-out infinite;
        display: inline-block;
      }
      #__gateTitle {
        font-size: 21px;
        font-weight: 800;
        color: #fff;
        margin-bottom: 10px;
        letter-spacing: -0.4px;
      }
      #__gateSub {
        font-size: 13.5px;
        color: rgba(255,255,255,0.55);
        line-height: 1.7;
        margin-bottom: 24px;
      }
      #__gateHint {
        background: rgba(160,216,179,0.10);
        border: 1px solid rgba(160,216,179,0.28);
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 20px;
        font-size: 13px;
        color: #a0d8b3;
        line-height: 1.6;
        text-align: left;
      }
      #__gateHint b {
        display: block;
        font-size: 14px;
        margin-bottom: 6px;
        color: #b8e6c7;
      }
      #__gateHint ol {
        margin: 0;
        padding-left: 18px;
        color: rgba(255,255,255,0.75);
      }
      #__gateHint ol li {
        margin-bottom: 3px;
      }
      #__goHomeBtn {
        width: 100%;
        padding: 16px 24px;
        border-radius: 999px;
        border: 1px solid rgba(160,216,179,0.35);
        background: rgba(160,216,179,0.15);
        color: #a0d8b3;
        font-size: 16px;
        font-weight: 700;
        cursor: pointer;
        font-family: inherit;
        transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.2s;
      }
      #__goHomeBtn:active {
        transform: scale(0.95);
        background: rgba(160,216,179,0.25);
      }
      #__gateFooter {
        margin-top: 18px;
        font-size: 11px;
        color: rgba(255,255,255,0.30);
        letter-spacing: 0.3px;
      }
    </style>

    <div id="__gateCard">
      <div id="__gateLock">🔒</div>
      <div id="__gateTitle">需要登录</div>
      <div id="__gateSub">${pageTitle}需要登录后才能使用</div>

      <div id="__gateHint">
        <b>💡 登录方式</b>
        <ol>
          <li>点下面的按钮回主页</li>
          <li>点主页<b style="display:inline;color:#b8e6c7;">右上角</b>"登录 →"</li>
          <li>登录成功后，再回到这里</li>
        </ol>
      </div>

      <button id="__goHomeBtn">🏠 回主页登录</button>
      <div id="__gateFooter">登录后可直接刷新本页</div>
    </div>
  `;
  document.body.appendChild(overlay);

  document.getElementById('__goHomeBtn').onclick = () => {
    if (navigator.vibrate) navigator.vibrate(12);
    // 直接替换历史，回主页
    location.replace('/');
  };
})();