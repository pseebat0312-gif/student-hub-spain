// 用户信息缓存
const __userInfoCache = {};

async function getUserInfo(email) {
  if (!email) return { nickname: '', emoji: '🐱', url: '' };
  if (__userInfoCache[email]) return __userInfoCache[email];
  try {
    const resp = await fetch('/api/profile?email=' + encodeURIComponent(email));
    const data = await resp.json();
    const info = {
      nickname: (data && data.nickname) || email.split('@')[0],
      emoji: (data && data.avatar_emoji) || '',
      url: (data && data.avatar_url) || ''
    };
    __userInfoCache[email] = info;
    return info;
  } catch (e) {
    const info = { nickname: email.split('@')[0], emoji: '🐱', url: '' };
    __userInfoCache[email] = info;
    return info;
  }
}

async function getManyUserInfo(emails) {
  const uniq = [...new Set((emails || []).filter(Boolean))];
  const result = {};
  await Promise.all(uniq.map(async e => {
    result[e] = await getUserInfo(e);
  }));
  return result;
}

function avatarHtml(info, size) {
  size = size || 24;
  if (info.url) {
    return `<img src="${info.url}" style="width:${size}px;height:${size}px;border-radius:50%;object-fit:cover;vertical-align:middle;display:inline-block;">`;
  }
  const emoji = info.emoji || '🐱';
  return `<span style="display:inline-block;width:${size}px;height:${size}px;line-height:${size}px;text-align:center;font-size:${Math.round(size*0.7)}px;vertical-align:middle;">${emoji}</span>`;
}

function nicknameOf(info, email) {
  return info.nickname || (email || '').split('@')[0] || '匿名';
}