from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for, g
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import socket, os, json, time, threading, sqlite3
import urllib.parse

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'cloud_settings.json')

# CORS strict selon le mode
mode = os.environ.get('METADIDOMI_SERVER_MODE', 'developpement')
if mode == 'production':
    domain = None
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            domain = data.get('domain_name')
    except Exception:
        pass
    if domain:
        cors_origins = [f"https://{domain}"]
    else:
        cors_origins = ["https://votre-domaine.com"]
else:
    cors_origins = ["*"]
CORS(app, origins=cors_origins, supports_credentials=True)

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_uploads'))
DOWNLOAD_LOG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'download_history.txt'))
os.makedirs(UPLOADS_DIR, exist_ok=True)

connected_users = {}
USERS_LOCK = threading.Lock()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'file_stats.db')

def ensure_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS file_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                action TEXT,
                ip TEXT,
                duration REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS file_user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                action TEXT,
                user_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(filename, action, user_id)
            )''')
            conn.commit()
ensure_db()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Ajout du champ user_id à la table
with sqlite3.connect(DB_PATH) as conn:
    try:
        conn.execute('ALTER TABLE file_stats ADD COLUMN user_id TEXT')
    except Exception:
        pass
    conn.commit()

def cleanup_users():
    while True:
        now = time.time()
        with USERS_LOCK:
            to_remove = [ip for ip, last in connected_users.items() if now - last > 60]
            for ip in to_remove:
                del connected_users[ip]
        socketio.emit('users_update', list(connected_users.keys()))
        time.sleep(30)

threading.Thread(target=cleanup_users, daemon=True).start()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def get_hostname():
    env = os.environ.get('METADIDOMI_HOSTNAME')
    if env:
        return env
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'hostname' in data and data['hostname']:
                return data['hostname']
    except Exception:
        pass
    return socket.gethostname()

HOSTNAME = get_hostname()

@app.route("/")
def index():
    ip = get_local_ip()
    try:
        files = [fname for fname in os.listdir(UPLOADS_DIR) if os.path.isfile(os.path.join(UPLOADS_DIR, fname))]
    except Exception:
        files = []
    return f"""
    <html><head><title>Metadidomi Server Plus</title></head><body>
    <h1>Bienvenue dans Metadidomi Server Plus <span style='color:#007bff;font-size:0.7em'></span></h1>
    </body></html>"""

@app.route('/files', methods=['GET', 'POST'])
def files_list():
    import datetime
    if request.method == 'POST':
        f = request.files.get('file')
        if f and f.filename:
            save_path = os.path.join(UPLOADS_DIR, f.filename)
            f.save(save_path)
            socketio.emit('files_update', get_files_list())
            return redirect(url_for('files_list'))
    files = []
    for fname in os.listdir(UPLOADS_DIR):
        fpath = os.path.join(UPLOADS_DIR, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            files.append({
                'name': fname,
                'size': stat.st_size,
                'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')
            })
    ip = get_local_ip()
    return render_template('cloud_files.html', files=files, hostname=HOSTNAME, ip=ip)

@app.route('/api/files')
def api_files():
    import datetime
    folder = request.args.get('folder')
    if not folder or folder == 'Root':
        base_dir = UPLOADS_DIR
    else:
        base_dir = os.path.join(UPLOADS_DIR, folder)
        if not os.path.isdir(base_dir):
            return jsonify({'files': []})
    files = []
    db = get_db()
    for fname in os.listdir(base_dir):
        fpath = os.path.join(base_dir, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="view"', (fname,))
            views = cur.fetchone()[0]
            cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="download"', (fname,))
            downloads = cur.fetchone()[0]
            cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="play"', (fname,))
            plays = cur.fetchone()[0]
            files.append({
                'name': fname,
                'size': stat.st_size,
                'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                'views': views,
                'downloads': downloads,
                'plays': plays
            })
    return jsonify({'files': files})

def get_files_list():
    import datetime
    try:
        files = []
        for fname in os.listdir(UPLOADS_DIR):
            fpath = os.path.join(UPLOADS_DIR, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                files.append({
                    'name': fname,
                    'size': stat.st_size,
                    'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')
                })
    except Exception:
        files = []
    return files

@app.route('/files/<filename>')
def download_file(filename):
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return jsonify({'error': 'Nom de fichier invalide'}), 400
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.isfile(file_path):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    ip = request.remote_addr
    log_download(ip, filename)
    socketio.emit('download_event', {'ip': ip, 'filename': filename, 'time': time.strftime('%d/%m/%Y %H:%M:%S')})
    return send_from_directory(UPLOADS_DIR, filename, as_attachment=True)

@app.route('/download/<path:filename>')
def download_file_compat(filename):
    safe_name = os.path.basename(urllib.parse.unquote(filename))
    file_path = os.path.join(UPLOADS_DIR, safe_name)
    if not os.path.isfile(file_path):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    ip = request.remote_addr
    log_download(ip, safe_name)
    socketio.emit('download_event', {'ip': ip, 'filename': safe_name, 'time': time.strftime('%d/%m/%Y %H:%M:%S')})
    return send_from_directory(UPLOADS_DIR, safe_name, as_attachment=True)

def log_download(ip, filename):
    entry = f"{time.strftime('%d/%m/%Y %H:%M:%S')} | {ip} | {filename}"
    with open(DOWNLOAD_LOG, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')

@app.route('/api/download_history')
def api_download_history():
    if not os.path.exists(DOWNLOAD_LOG):
        return jsonify({'history': []})
    with open(DOWNLOAD_LOG, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return jsonify({'history': [line.strip() for line in lines[-100:]]})

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    safe_name = os.path.basename(urllib.parse.unquote(filename))
    fpath = os.path.join(UPLOADS_DIR, safe_name)
    if os.path.isfile(fpath):
        os.remove(fpath)
        with sqlite3.connect(DB_PATH) as conn:
            tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            for table in tables:
                cols_info = conn.execute(f"PRAGMA table_info({table})").fetchall()
                text_cols = [col[1] for col in cols_info if col[2] in ('TEXT', 'VARCHAR', 'CHAR')]
                for col in text_cols:
                    try:
                        conn.execute(f"DELETE FROM {table} WHERE {col} LIKE ?", (f"%{safe_name}%",))
                    except Exception:
                        pass
            conn.commit()
        socketio.emit('files_update', get_files_list())
    return redirect(url_for('files_list'))

@socketio.on('connect')
def handle_connect():
    ip = request.remote_addr
    with USERS_LOCK:
        connected_users[ip] = time.time()
    emit('users_update', list(connected_users.keys()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    ip = request.remote_addr
    with USERS_LOCK:
        if ip in connected_users:
            del connected_users[ip]
    emit('users_update', list(connected_users.keys()), broadcast=True)

@socketio.on('ping_user')
def handle_ping():
    ip = request.remote_addr
    with USERS_LOCK:
        connected_users[ip] = time.time()
    emit('users_update', list(connected_users.keys()), broadcast=True)

def get_user_id():
    return request.remote_addr

@app.route('/api/increment_view', methods=['POST'])
def api_increment_view():
    data = request.get_json(force=True)
    name = data.get('name')
    type_ = data.get('type')
    duration = float(data.get('duration', 0))
    user_id = get_user_id()
    if not name or not type_:
        return jsonify({'error': 'missing name/type'}), 400
    db = get_db()
    if type_ == 'download':
        action = 'download'
    elif type_ == 'play' or type_ == 'audio':
        action = 'play'
    else:
        action = 'view'
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action=? AND user_id=?',
                     (name, action, user_id))
    already = cur.fetchone()[0]
    if already == 0:
        db.execute('INSERT INTO file_user_actions (filename, action, user_id) VALUES (?, ?, ?)', (name, action, user_id))
        db.execute('INSERT INTO file_stats (filename, action, ip, duration, user_id) VALUES (?, ?, ?, ?, ?)', (name, action, request.remote_addr, duration, user_id))
        db.commit()
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="view"', (name,))
    views = cur.fetchone()[0]
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="download"', (name,))
    downloads = cur.fetchone()[0]
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="play"', (name,))
    plays = cur.fetchone()[0]
    return jsonify({'ok': True, 'views': views, 'downloads': downloads, 'plays': plays})

if __name__ == "__main__":
    ip = get_local_ip()
    print(f"Serveur démarré sur : http://{ip}:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
