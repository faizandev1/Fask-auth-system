import os, csv, random, string, hashlib, smtplib, uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash)
from functools import wraps
from dotenv import load_dotenv

load_dotenv()  # reads .env file

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

DATA_DIR = 'data'
USERS_FILE   = os.path.join(DATA_DIR, 'users.csv')
LOGS_FILE    = os.path.join(DATA_DIR, 'logs.csv')
TOKENS_FILE  = os.path.join(DATA_DIR, 'tokens.csv')
OTP_FILE     = os.path.join(DATA_DIR, 'otps.csv')

os.makedirs(DATA_DIR, exist_ok=True)

USER_HEADERS  = ['id','first_name','last_name','email','password_hash','dob','created_at','is_verified','two_fa_enabled','auto_logout_minutes']
LOG_HEADERS   = ['timestamp','email','action','ip','status','details']
TOKEN_HEADERS = ['token','email','type','created_at','expires_at','used']
OTP_HEADERS   = ['email','otp','created_at','expires_at','used']

def init_csv():
    pairs = [(USERS_FILE,USER_HEADERS),(LOGS_FILE,LOG_HEADERS),(TOKENS_FILE,TOKEN_HEADERS),(OTP_FILE,OTP_HEADERS)]
    for fp, hdrs in pairs:
        if not os.path.exists(fp):
            with open(fp,'w',newline='',encoding='utf-8') as f:
                csv.writer(f).writerow(hdrs)

init_csv()

# ── CSV helpers ────────────────────────────────────────────────────────────────

def read_csv(fp):
    rows = []
    try:
        with open(fp,'r',newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f):
                rows.append(dict(row))
    except: pass
    return rows

def write_csv(fp, rows, headers):
    with open(fp,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader(); w.writerows(rows)

def append_csv(fp, row):
    exists = os.path.exists(fp)
    with open(fp,'a',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists: w.writeheader()
        w.writerow(row)

# ── User helpers ───────────────────────────────────────────────────────────────

def get_user(email):
    for u in read_csv(USERS_FILE):
        if u['email'].lower() == email.lower():
            return u
    return None

def save_user(user):
    users = read_csv(USERS_FILE)
    updated = False
    for i,u in enumerate(users):
        if u['email'].lower() == user['email'].lower():
            users[i] = user; updated = True; break
    if not updated: users.append(user)
    write_csv(USERS_FILE, users, USER_HEADERS)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Logging ────────────────────────────────────────────────────────────────────

def log_action(email, action, status, details=''):
    append_csv(LOGS_FILE,{
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': email, 'action': action,
        'ip': request.remote_addr, 'status': status, 'details': details
    })

# ── OTP helpers ────────────────────────────────────────────────────────────────

def gen_otp(): return ''.join([str(random.randint(0,9)) for _ in range(6)])

def save_otp(email, otp):
    otps = read_csv(OTP_FILE)
    for o in otps:
        if o['email'].lower() == email.lower():
            o['used'] = 'true'
    now = datetime.now()
    otps.append({'email':email,'otp':otp,
        'created_at':now.strftime('%Y-%m-%d %H:%M:%S'),
        'expires_at':(now+timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S'),
        'used':'false'})
    write_csv(OTP_FILE, otps, OTP_HEADERS)

def verify_otp_code(email, code):
    otps = read_csv(OTP_FILE)
    now = datetime.now()
    for o in reversed(otps):
        if o['email'].lower()==email.lower() and o['used']=='false' and o['otp']==code:
            if now <= datetime.strptime(o['expires_at'],'%Y-%m-%d %H:%M:%S'):
                o['used']='true'
                write_csv(OTP_FILE, otps, OTP_HEADERS)
                return True
    return False

# ── Token helpers ──────────────────────────────────────────────────────────────

def create_token(email, ttype, hrs=1):
    token = str(uuid.uuid4())
    now = datetime.now()
    append_csv(TOKENS_FILE,{'token':token,'email':email,'type':ttype,
        'created_at':now.strftime('%Y-%m-%d %H:%M:%S'),
        'expires_at':(now+timedelta(hours=hrs)).strftime('%Y-%m-%d %H:%M:%S'),
        'used':'false'})
    return token

def verify_token(token, ttype):
    now = datetime.now()
    for t in read_csv(TOKENS_FILE):
        if t['token']==token and t['type']==ttype and t['used']=='false':
            if now <= datetime.strptime(t['expires_at'],'%Y-%m-%d %H:%M:%S'):
                return t['email']
    return None

def consume_token(token):
    tokens = read_csv(TOKENS_FILE)
    for t in tokens:
        if t['token']==token: t['used']='true'
    write_csv(TOKENS_FILE, tokens, TOKEN_HEADERS)

# ── Email ──────────────────────────────────────────────────────────────────────

def send_email(to, subject, html):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'AuthSystem <{EMAIL_ADDRESS}>'
        msg['To'] = to
        msg.attach(MIMEText(html,'html'))
        with smtplib.SMTP('smtp.gmail.com',587) as s:
            s.starttls(); s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.sendmail(EMAIL_ADDRESS, to, msg.as_string())
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}'); return False

def send_otp_email(to, otp, name=''):
    html = render_template('email/otp_email.html', otp=otp, name=name, year=datetime.now().year)
    return send_email(to, 'Your Verification Code — AuthSystem', html)

def send_reset_email(to, link, temp_pw, name=''):
    html = render_template('email/reset_email.html', link=link, temp_pw=temp_pw, name=name, year=datetime.now().year)
    return send_email(to, 'Reset Your Password — AuthSystem', html)

# ── Auth decorator ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*a,**kw)
    return dec

# ── CAPTCHA ────────────────────────────────────────────────────────────────────

def gen_captcha():
    c = str(random.randint(10000,99999))
    session['captcha'] = c
    return c

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_email' in session else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email    = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        user     = get_user(email)
        if not user:
            log_action(email,'LOGIN','FAILED','User not found')
            flash('Invalid email or password.','error')
            return render_template('login.html')
        if user['is_verified']!='true':
            flash('Please verify your email first. Check your inbox.','warning')
            session['pending_email']=email; session['otp_purpose']='signup'
            return redirect(url_for('verify_otp_page'))
        if user['password_hash']!=hash_pw(password):
            log_action(email,'LOGIN','FAILED','Wrong password')
            flash('Invalid email or password.','error')
            return render_template('login.html')
        if user.get('two_fa_enabled','true')=='true':
            otp=gen_otp(); save_otp(email,otp)
            send_otp_email(email,otp,user['first_name'])
            session['pending_email']=email; session['otp_purpose']='login'
            return redirect(url_for('verify_otp_page'))
        session['user_email']=email
        session['user_name']=f"{user['first_name']} {user['last_name']}"
        log_action(email,'LOGIN','SUCCESS','Direct login')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        fn  = request.form.get('first_name','').strip()
        ln  = request.form.get('last_name','').strip()
        em  = request.form.get('email','').strip().lower()
        pw  = request.form.get('password','')
        cpw = request.form.get('confirm_password','')
        dob = request.form.get('dob','')
        cap = request.form.get('captcha','')
        agr = request.form.get('agree')
        errors=[]
        if not all([fn,ln,em,pw,dob]): errors.append('All fields are required.')
        if pw!=cpw: errors.append('Passwords do not match.')
        if len(pw)<8: errors.append('Password must be at least 8 characters.')
        if cap!=session.get('captcha',''): errors.append('CAPTCHA verification failed.')
        if not agr: errors.append('You must agree to the Terms and Conditions.')
        if get_user(em): errors.append('This email is already registered.')
        if errors:
            for e in errors: flash(e,'error')
            return render_template('signup.html',captcha=gen_captcha())
        user={'id':str(uuid.uuid4()),'first_name':fn,'last_name':ln,'email':em,
              'password_hash':hash_pw(pw),'dob':dob,
              'created_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              'is_verified':'false','two_fa_enabled':'true','auto_logout_minutes':'5'}
        save_user(user)
        otp=gen_otp(); save_otp(em,otp); send_otp_email(em,otp,fn)
        session['pending_email']=em; session['otp_purpose']='signup'
        log_action(em,'SIGNUP','SUCCESS')
        return redirect(url_for('verify_otp_page'))
    return render_template('signup.html',captcha=gen_captcha())

@app.route('/verify-otp', methods=['GET','POST'])
def verify_otp_page():
    if 'pending_email' not in session:
        return redirect(url_for('login'))
    if request.method=='POST':
        otp_in=''.join([request.form.get(f'otp{i}','') for i in range(1,7)])
        email  = session['pending_email']
        purpose= session.get('otp_purpose','signup')
        if verify_otp_code(email,otp_in):
            user=get_user(email)
            if purpose=='signup':
                user['is_verified']='true'; save_user(user)
            session.pop('pending_email',None)
            session['user_email']=email
            session['user_name']=f"{user['first_name']} {user['last_name']}"
            log_action(email,'OTP_VERIFY','SUCCESS',purpose)
            flash('Welcome! You\'re now signed in.','success')
            return redirect(url_for('dashboard'))
        else:
            log_action(session['pending_email'],'OTP_VERIFY','FAILED')
            flash('Invalid or expired code. Please try again.','error')
    return render_template('otp.html', email=session.get('pending_email',''))

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    email=session.get('pending_email')
    if not email: return jsonify({'success':False,'msg':'Session expired'})
    user=get_user(email)
    otp=gen_otp(); save_otp(email,otp)
    ok=send_otp_email(email,otp,user['first_name'] if user else '')
    log_action(email,'OTP_RESEND','SUCCESS' if ok else 'FAILED')
    return jsonify({'success':ok})

@app.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower()
        dob  =request.form.get('dob','')
        user =get_user(email)
        if user and user['dob']==dob:
            token=create_token(email,'reset',hrs=1)
            temp_pw=''.join(random.choices(string.ascii_letters+string.digits,k=8))
            session[f'tmp_{token}']=hash_pw(temp_pw)
            link=url_for('reset_password',token=token,_external=True)
            send_reset_email(email,link,temp_pw,user['first_name'])
            log_action(email,'FORGOT_PASSWORD','SUCCESS')
            flash('A reset link has been sent to your email.','success')
            return render_template('forgot_password.html',sent=True)
        else:
            log_action(email,'FORGOT_PASSWORD','FAILED','Invalid email or DOB')
            flash('Email or date of birth is incorrect.','error')
    return render_template('forgot_password.html',sent=False)

@app.route('/reset-password/<token>', methods=['GET','POST'])
def reset_password(token):
    email=verify_token(token,'reset')
    if not email:
        flash('This reset link is invalid or has expired.','error')
        return redirect(url_for('login'))
    if request.method=='POST':
        tmp_in  =request.form.get('temp_password','')
        new_pw  =request.form.get('new_password','')
        conf_pw =request.form.get('confirm_password','')
        stored  =session.get(f'tmp_{token}')
        if stored and stored!=hash_pw(tmp_in):
            flash('Temporary password is incorrect.','error')
            return render_template('reset_password.html',token=token)
        if new_pw!=conf_pw:
            flash('Passwords do not match.','error')
            return render_template('reset_password.html',token=token)
        if len(new_pw)<8:
            flash('Password must be at least 8 characters.','error')
            return render_template('reset_password.html',token=token)
        user=get_user(email); user['password_hash']=hash_pw(new_pw)
        save_user(user); consume_token(token)
        session.pop(f'tmp_{token}',None)
        log_action(email,'PASSWORD_RESET','SUCCESS')
        flash('Password reset successfully! Please sign in.','success')
        return redirect(url_for('login'))
    return render_template('reset_password.html',token=token)

@app.route('/dashboard')
@login_required
def dashboard():
    email=session['user_email']; user=get_user(email)
    all_logs=read_csv(LOGS_FILE)
    user_logs=[l for l in all_logs if l['email'].lower()==email.lower()]
    return render_template('dashboard.html',user=user,logs=list(reversed(user_logs[-30:])))

@app.route('/settings', methods=['POST'])
@login_required
def settings():
    email=session['user_email']; user=get_user(email)
    user['two_fa_enabled']='true' if request.form.get('two_fa')=='on' else 'false'
    minutes=request.form.get('auto_logout_minutes','5')
    user['auto_logout_minutes']=minutes if minutes.isdigit() and int(minutes)>=1 else '5'
    save_user(user); log_action(email,'SETTINGS_UPDATE','SUCCESS')
    flash('Settings saved successfully.','success')
    return redirect(url_for('dashboard'))

@app.route('/api/settings')
@login_required
def api_settings():
    user=get_user(session['user_email'])
    return jsonify({'two_fa_enabled':user.get('two_fa_enabled','true'),
                    'auto_logout_minutes':user.get('auto_logout_minutes','5')})

@app.route('/api/ask', methods=['POST'])
@login_required
def api_ask():
    q=request.json.get('question','').strip()
    if not q: return jsonify({'answer':'Please type a question.'})
    # Simple FAQ engine — user can expand
    faq = {
        'how do i change my password': 'Go to Settings tab → Security section → click Change Password.',
        'how do i enable 2fa': 'Go to Settings tab → toggle "Two-Factor Authentication" to ON.',
        'how do i logout': 'Click the Logout button in the top right corner.',
        'what is auto logout': 'Auto logout signs you out after a period of inactivity. You can set the timer in Settings.',
    }
    ql=q.lower()
    for k,v in faq.items():
        if any(w in ql for w in k.split()):
            return jsonify({'answer':v})
    return jsonify({'answer':f'I received your question: "{q}". This assistant can answer questions about account settings, security, and navigation. Try asking about 2FA, auto-logout, or password changes.'})

@app.route('/logout')
def logout():
    email=session.get('user_email','')
    log_action(email,'LOGOUT','SUCCESS')
    session.clear()
    return redirect(url_for('login'))

@app.route('/refresh-captcha')
def refresh_captcha():
    return jsonify({'captcha':gen_captcha()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
