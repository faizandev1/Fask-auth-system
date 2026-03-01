// ═══════════════════════════════════════════════════
//   AUTHSYSTEM Dashboard JavaScript
// ═══════════════════════════════════════════════════

// ── Tab Navigation ────────────────────────────────────

const navItems  = document.querySelectorAll('.nav-item[data-tab]');
const tabPanels = document.querySelectorAll('.tab-panel');
const topbarTitle = document.getElementById('topbarTitle');
const titles = { home: 'Home', ask: 'Ask AI', logs: 'Activity Logs', settings: 'Settings' };

function switchTab(tabId) {
  navItems.forEach(n => n.classList.toggle('active', n.dataset.tab === tabId));
  tabPanels.forEach(p => p.classList.toggle('active', p.id === `tab-${tabId}`));
  if (topbarTitle) topbarTitle.textContent = titles[tabId] || '';
}

navItems.forEach(item => {
  item.addEventListener('click', e => { e.preventDefault(); switchTab(item.dataset.tab); });
});

// "View all →" button in recent logs
document.querySelectorAll('[data-tab="logs"]').forEach(btn => {
  btn.addEventListener('click', () => switchTab('logs'));
});

// ── Sidebar Toggle (mobile) ───────────────────────────

const sidebar = document.getElementById('sidebar');
const toggle  = document.getElementById('sidebarToggle');
if (toggle && sidebar) {
  toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== toggle) {
      sidebar.classList.remove('open');
    }
  });
}

// ── Auto-Logout ───────────────────────────────────────

const AUTO_MINS = typeof AUTO_LOGOUT_MINUTES !== 'undefined' ? AUTO_LOGOUT_MINUTES : 5;
const IDLE_MS   = AUTO_MINS > 0 ? AUTO_MINS * 60 * 1000 : null;
const WARN_MS   = 30 * 1000; // warn 30s before logout

const modal          = document.getElementById('autoLogoutModal');
const logoutCountEl  = document.getElementById('logoutCountdown');
const stayBtn        = document.getElementById('stayBtn');
const idleIndicator  = document.getElementById('idleIndicator');
const idleLabel      = document.getElementById('idleLabel');
const idleDot        = idleIndicator?.querySelector('.idle-dot');

let idleTimer    = null;
let logoutTimer  = null;
let logoutCount  = 30;
let logoutInterval = null;

function resetIdle() {
  if (!IDLE_MS) return;
  clearTimeout(idleTimer);
  clearTimeout(logoutTimer);
  clearInterval(logoutInterval);
  if (modal) modal.style.display = 'none';
  if (idleDot) { idleDot.className = 'idle-dot active'; }
  if (idleLabel) idleLabel.textContent = 'Active';

  idleTimer = setTimeout(showWarning, IDLE_MS - WARN_MS);
}

function showWarning() {
  if (!modal) return;
  modal.style.display = 'flex';
  logoutCount = 30;
  if (logoutCountEl) logoutCountEl.textContent = logoutCount;
  if (idleDot) { idleDot.className = 'idle-dot warning'; }
  if (idleLabel) idleLabel.textContent = 'Idle';

  logoutInterval = setInterval(() => {
    logoutCount--;
    if (logoutCountEl) logoutCountEl.textContent = logoutCount;
    if (logoutCount <= 0) {
      clearInterval(logoutInterval);
      window.location.href = '/logout';
    }
  }, 1000);
}

if (stayBtn) {
  stayBtn.addEventListener('click', () => {
    clearInterval(logoutInterval);
    if (modal) modal.style.display = 'none';
    resetIdle();
  });
}

// Track user activity
['mousemove','keydown','click','scroll','touchstart'].forEach(evt => {
  document.addEventListener(evt, resetIdle, { passive: true });
});

if (IDLE_MS) {
  resetIdle(); // start timer
} else {
  if (idleLabel) idleLabel.textContent = 'No timeout';
}

// ── Chat / Ask AI ─────────────────────────────────────

const chatWindow  = document.getElementById('chatWindow');
const chatInput   = document.getElementById('chatInput');
const chatSend    = document.getElementById('chatSend');

function appendMessage(text, role) {
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${role === 'user' ? 'user-bubble' : 'bot-bubble'}`;
  bubble.innerHTML = `
    <div class="chat-avatar-dot">${role === 'user' ? 'Me' : 'AI'}</div>
    <div class="chat-text">${text}</div>
  `;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendThinking() {
  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble bot-bubble chat-thinking';
  bubble.id = 'thinkingBubble';
  bubble.innerHTML = `<div class="chat-avatar-dot">AI</div><div class="chat-text">Thinking…</div>`;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(text) {
  if (!text.trim()) return;
  appendMessage(text, 'user');
  if (chatInput) chatInput.value = '';
  appendThinking();

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text })
    });
    const data = await res.json();
    const thinking = document.getElementById('thinkingBubble');
    if (thinking) thinking.remove();
    appendMessage(data.answer || 'Sorry, I could not process that.', 'bot');
  } catch {
    const thinking = document.getElementById('thinkingBubble');
    if (thinking) thinking.remove();
    appendMessage('Connection error. Please try again.', 'bot');
  }
}

if (chatSend) {
  chatSend.addEventListener('click', () => sendMessage(chatInput?.value || ''));
}
if (chatInput) {
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(chatInput.value);
    }
  });
}

// Suggestion chips
document.querySelectorAll('.suggestion-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    switchTab('ask');
    sendMessage(chip.dataset.q);
  });
});

// ── Settings 2FA instant feedback ────────────────────

const twoFaToggle = document.getElementById('twoFaToggle');
if (twoFaToggle) {
  twoFaToggle.addEventListener('change', () => {
    const s = twoFaToggle.closest('.setting-row')?.querySelector('.setting-name');
    if (s) s.textContent = 'Two-Factor Authentication ' + (twoFaToggle.checked ? '(will be enabled)' : '(will be disabled)');
  });
}
