// static/js/vip-gate.js
// 通用 VIP 试用 / 锁定 / 引导逻辑
// 用法：页面里放一个按钮，给它 data-feature="ai_detect"，然后调 VipGate.run(...)

window.VipGate = (function () {
  function getEmail() {
    return (localStorage.getItem('user_email') || '').trim().toLowerCase();
  }
  function getToken() {
    return localStorage.getItem('access_token') || '';
  }

  // 查询当前功能的状态
  async function check(feature) {
    const email = getEmail();
    if (!email) return { is_vip: false, remaining: 0, need_login: true };
    try {
      const r = await fetch(
        '/api/vip/check_usage?email=' + encodeURIComponent(email) +
        '&feature=' + encodeURIComponent(feature) +
        '&t=' + Date.now()
      );
      const d = await r.json();
      return d;
    } catch (e) {
      return { is_vip: false, remaining: 0, error: true };
    }
  }

  // 消耗一次
  async function consume(feature) {
    const email = getEmail();
    if (!email) return { error: '请先登录', need_login: true };
    try {
      const r = await fetch('/api/vip/consume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, feature })
      });
      const d = await r.json();
      if (!r.ok) {
        // 403 = 免费次数用完
        return { ...d, http_status: r.status };
      }
      return d;
    } catch (e) {
      return { error: '网络错误' };
    }
  }

  // 弹窗：免费次数用完，引导去 VIP
  function showLockModal(featureName) {
    const old = document.getElementById('vipLockModal');
    if (old) old.remove();

    const div = document.createElement('div');
    div.id = 'vipLockModal';
    div.style.cssText = `
      position: fixed; inset: 0; z-index: 99999;
      background: rgba(0,0,0,0.6);
      backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
      display: flex; align-items: center; justify-content: center;
      padding: 20px; animation: vipFadeIn .25s ease;
    `;
    div.innerHTML = `
      <div style="
        width: 100%; max-width: 360px;
        background: #1c1c1e; border-radius: 22px;
        padding: 26px 22px 22px; color: #fff;
        font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      ">
        <div style="font-size: 44px; text-align: center; margin-bottom: 8px;">👑</div>
        <div style="font-size: 18px; font-weight: 800; text-align: center; margin-bottom: 8px;">
          免费次数已用完
        </div>
        <div style="font-size: 13px; color: rgba(255,255,255,0.6); line-height: 1.6; text-align: center; margin-bottom: 20px;">
          ${featureName || '该功能'}免费试用 3 次已用完。<br>
          开通 VIP 后可无限次使用。
        </div>
        <button id="vipLockGo" style="
          width: 100%; padding: 15px; border-radius: 999px; border: none;
          background: linear-gradient(135deg, #e8a8b8, #c98094);
          color: #1a0f14; font-size: 15px; font-weight: 700;
          cursor: pointer; font-family: inherit; margin-bottom: 10px;
        ">立即开通 VIP →</button>
        <button id="vipLockClose" style="
          width: 100%; padding: 12px; border-radius: 999px;
          border: 1px solid rgba(255,255,255,0.12);
          background: transparent; color: rgba(255,255,255,0.55);
          font-size: 13px; font-weight: 600; cursor: pointer;
          font-family: inherit;
        ">以后再说</button>
      </div>
      <style>@keyframes vipFadeIn{from{opacity:0}to{opacity:1}}</style>
    `;
    document.body.appendChild(div);
    document.getElementById('vipLockGo').onclick = () => {
      location.href = '/vip';
    };
    document.getElementById('vipLockClose').onclick = () => div.remove();
    div.addEventListener('click', (e) => { if (e.target === div) div.remove(); });
  }

  // 主入口：点按钮时调用
  // 用法：VipGate.run('ai_detect', 'AI 检测', async () => { ...真正干活的代码... })
  async function run(feature, featureName, onAllowed) {
    const email = getEmail();
    if (!email) {
      alert('请先登录');
      location.href = '/login';
      return;
    }
    // 先查状态
    const st = await check(feature);
    if (st.is_vip) {
      // VIP 直接放行
      if (typeof onAllowed === 'function') onAllowed();
      return;
    }
    if ((st.remaining || 0) <= 0) {
      showLockModal(featureName);
      return;
    }
    // 还有次数 → 消耗一次
    const res = await consume(feature);
    if (res.success) {
      if (typeof onAllowed === 'function') onAllowed();
    } else if (res.need_vip || res.http_status === 403) {
      showLockModal(featureName);
    } else {
      alert(res.error || '操作失败');
    }
  }

  // 给页面用的：刷新按钮上的“剩余 X 次”文案
  async function updateBadge(el, feature) {
    if (!el) return;
    const email = getEmail();
    if (!email) { el.textContent = ''; return; }
    const st = await check(feature);
    if (st.is_vip) { el.textContent = '👑 VIP 无限'; el.style.color = '#e8a8b8'; return; }
    if (typeof st.remaining === 'number') {
      el.textContent = `免费剩余 ${st.remaining} / ${st.limit || 3} 次`;
      el.style.color = st.remaining > 0 ? 'rgba(255,255,255,0.6)' : '#ff8080';
    }
  }

  return { run, check, consume, showLockModal, updateBadge, getEmail };
})();