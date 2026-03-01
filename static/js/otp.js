// ── OTP Box Behavior ──────────────────────────────────

const boxes = document.querySelectorAll('.otp-box');
const verifyBtn = document.getElementById('verifyBtn');

function checkAllFilled() {
  const allFilled = [...boxes].every(b => b.value.trim() !== '');
  if (verifyBtn) verifyBtn.disabled = !allFilled;
}

boxes.forEach((box, idx) => {
  box.addEventListener('input', e => {
    const val = e.target.value.replace(/\D/g, '');
    box.value = val.slice(-1);
    if (val) {
      box.classList.add('filled');
      if (idx < boxes.length - 1) boxes[idx + 1].focus();
    } else {
      box.classList.remove('filled');
    }
    checkAllFilled();
  });

  box.addEventListener('keydown', e => {
    if (e.key === 'Backspace' && !box.value && idx > 0) {
      boxes[idx - 1].value = '';
      boxes[idx - 1].classList.remove('filled');
      boxes[idx - 1].focus();
      checkAllFilled();
    }
    if (e.key === 'ArrowLeft' && idx > 0) boxes[idx - 1].focus();
    if (e.key === 'ArrowRight' && idx < boxes.length - 1) boxes[idx + 1].focus();
  });

  box.addEventListener('paste', e => {
    e.preventDefault();
    const text = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g,'');
    text.split('').slice(0, boxes.length).forEach((ch, i) => {
      boxes[i].value = ch;
      boxes[i].classList.add('filled');
    });
    const next = Math.min(text.length, boxes.length - 1);
    boxes[next].focus();
    checkAllFilled();
  });
});

if (boxes.length > 0) boxes[0].focus();

// ── Countdown Timer ───────────────────────────────────

let seconds = 60;
const countdownEl = document.getElementById('countdown');
const timerText   = document.getElementById('timerText');
const resendBtn   = document.getElementById('resendBtn');

const timer = setInterval(() => {
  seconds--;
  if (countdownEl) countdownEl.textContent = seconds;
  if (seconds <= 0) {
    clearInterval(timer);
    if (timerText)  timerText.style.display = 'none';
    if (resendBtn)  resendBtn.style.display = 'inline-block';
  }
}, 1000);

// ── Resend OTP ────────────────────────────────────────

if (resendBtn) {
  resendBtn.addEventListener('click', async () => {
    resendBtn.disabled = true;
    resendBtn.textContent = 'Sending…';
    try {
      const res = await fetch('/resend-otp', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        resendBtn.textContent = '✓ Sent!';
        // reset boxes
        boxes.forEach(b => { b.value = ''; b.classList.remove('filled'); });
        if (verifyBtn) verifyBtn.disabled = true;
        boxes[0].focus();
        // restart timer
        seconds = 60;
        if (timerText)  timerText.style.display = '';
        if (resendBtn)  resendBtn.style.display = 'none';
        if (countdownEl) countdownEl.textContent = 60;
        const newTimer = setInterval(() => {
          seconds--;
          if (countdownEl) countdownEl.textContent = seconds;
          if (seconds <= 0) {
            clearInterval(newTimer);
            if (timerText)  timerText.style.display = 'none';
            resendBtn.style.display = 'inline-block';
            resendBtn.disabled = false;
            resendBtn.textContent = 'Resend Code';
          }
        }, 1000);
      } else {
        resendBtn.textContent = 'Try again';
        resendBtn.disabled = false;
      }
    } catch {
      resendBtn.textContent = 'Error. Try again';
      resendBtn.disabled = false;
    }
  });
}
