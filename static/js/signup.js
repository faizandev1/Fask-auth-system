// ── Password Strength ─────────────────────────────────

const pw1 = document.getElementById('pw1');
const pw2 = document.getElementById('pw2');
const bar = document.getElementById('pwBar');
const lbl = document.getElementById('pwStrengthLabel');
const matchIcon = document.getElementById('pwMatchIcon');

function strengthScore(pw) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

if (pw1) {
  pw1.addEventListener('input', () => {
    const s = strengthScore(pw1.value);
    const pct = [0, 20, 40, 65, 85, 100][s];
    const colors = ['', '#ea4335', '#f59e0b', '#f59e0b', '#34a853', '#1a73e8'];
    const labels = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    if (bar) { bar.style.width = pct + '%'; bar.style.background = colors[s]; }
    if (lbl) { lbl.textContent = pw1.value ? labels[s] : ''; lbl.style.color = colors[s]; }
    checkMatch();
  });
}

function checkMatch() {
  if (!pw2 || !pw1 || !matchIcon) return;
  if (!pw2.value) { matchIcon.innerHTML = ''; return; }
  if (pw1.value === pw2.value) {
    matchIcon.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34a853" stroke-width="3"><polyline points="20,6 9,17 4,12"/></svg>`;
    pw2.style.borderColor = '#34a853';
  } else {
    matchIcon.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ea4335" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
    pw2.style.borderColor = '#ea4335';
  }
}
if (pw2) pw2.addEventListener('input', checkMatch);

// ── CAPTCHA Refresh ───────────────────────────────────

const refreshBtn = document.getElementById('refreshCaptcha');
const captchaDisplay = document.getElementById('captchaDisplay');
const captchaInput = document.getElementById('captchaInput');

if (refreshBtn) {
  refreshBtn.addEventListener('click', async () => {
    refreshBtn.style.transform = 'rotate(180deg)';
    try {
      const res = await fetch('/refresh-captcha');
      const data = await res.json();
      if (captchaDisplay) {
        captchaDisplay.innerHTML = `<span class="captcha-noise">${data.captcha}</span>`;
      }
      if (captchaInput) captchaInput.value = '';
      captchaInput.focus();
    } catch(e) { console.error(e); }
    setTimeout(() => { refreshBtn.style.transform = ''; }, 300);
  });
}

// ── Form submit button state ──────────────────────────

const form = document.getElementById('signupForm');
if (form) {
  form.addEventListener('submit', () => {
    const btn = document.getElementById('submitBtn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span>Creating account…</span>';
    }
  });
}
