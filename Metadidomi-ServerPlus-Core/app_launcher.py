from pathlib import Path
import subprocess
import sys
import os
import socket
import threading
import webbrowser
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import json
import psutil
import requests
HERE = Path(__file__).parent
flask_process = None

# ---------- Utilities ----------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def get_flask_cmd():
    env = os.environ.copy()
    cmd = [sys.executable, str(HERE / 'app' / 'flask_app.py')]
    return cmd, env

# ---------- Process control ----------
if not (HERE / 'logs.txt').exists():
    with open(HERE / 'logs.txt', 'w', encoding='utf-8') as f:
        f.write('')

def start_flask(output_callback=None):
    global flask_process
    if flask_process is None or flask_process.poll() is not None:
        cmd, env = get_flask_cmd()
        flask_process = subprocess.Popen(cmd, cwd=str(HERE), env=env, stdout=None, stderr=None)
        if output_callback:
            output_callback('Serveur Web démarré')

def stop_flask(output_callback=None):
    global flask_process
    if flask_process and flask_process.poll() is None:
        try:
            parent = psutil.Process(flask_process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            gone, alive = psutil.wait_procs([parent] + parent.children(recursive=True), timeout=5)
        except Exception:
            flask_process.terminate()
        if output_callback:
            output_callback('Serveur Web arrêté')

# ---------- GUI ----------
class LauncherUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.ip = get_local_ip()
        self._make_style()
        self._build_ui()
        self.update_buttons()
        self._init_socketio()
        self._last_log_pos = 0
        self._last_log_size = 0

    def _init_socketio(self):
        import socketio
        self.sio = socketio.Client()
        self.sio.on('users_update', self._on_users_update)
        self.sio.on('download_event', self._on_download_event)
        def connect_thread():
            try:
                self.sio.connect(f'http://{self.ip}:5000', transports=['websocket'])
            except Exception:
                pass
        threading.Thread(target=connect_thread, daemon=True).start()

    def _on_users_update(self, users):
        def update():
            self.flask_users_list.delete(0, 'end')
            for u in users:
                self.flask_users_list.insert('end', u)
        self.master.after(0, update)

    def _on_download_event(self, data):
        def update():
            line = f"{data.get('time','')} | {data.get('ip','')} | {data.get('filename','')}"
            self.flask_downloads_list.config(state='normal')
            self.flask_downloads_list.insert('end', line + '\n')
            self.flask_downloads_list.config(state='disabled')
        self.master.after(0, update)

    def _make_style(self):
        style = ttk.Style()
        for theme in ('vista', 'winnative', 'clam'):
            try:
                style.theme_use(theme)
                break
            except Exception:
                pass
        default_font = ('Segoe UI', 10)
        self.master.option_add('*Font', default_font)
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Card.TLabelframe', background='#ffffff')
        style.configure('TButton', padding=6)

    def _build_ui(self):
        container = ttk.Frame(self, padding=(12,12,12,12))
        container.pack(fill='both', expand=True)
        nb = ttk.Notebook(container)
        nb.pack(fill='both', expand=True, pady=(12,0))
        self.flask_tab = ttk.Frame(nb)
        nb.add(self.flask_tab, text='Serveur Web')
        self._build_flask_tab(self.flask_tab)
        # Footer
        footer = ttk.Frame(container)
        footer.pack(fill='x', pady=(12,0))
        ttk.Separator(footer, orient='horizontal').pack(fill='x', pady=(0,8))
        ttk.Label(footer, text='© 2025 Metadidomi Server Plus (Version simplifiée)').pack(side='left')
        self.global_statusbar = ttk.Label(footer, text='', anchor='e', foreground='#007bff')
        self.global_statusbar.pack(side='right', padx=(0, 4))

    def _build_flask_tab(self, parent):
        card = ttk.Labelframe(parent, text='Serveur de transfert de fichiers', padding=12, style='Card.TLabelframe')
        card.pack(fill='x', padx=8, pady=8)
        ttk.Label(card, text=f'Adresse : http://{self.ip}:5000/files').pack(anchor='w')
        self.flask_status = ttk.Label(card, text='Arrêté', foreground='#dc3545', font=('Segoe UI', 11, 'bold'))
        self.flask_status.pack(anchor='w', pady=(4,8))
        btnframe = ttk.Frame(card)
        btnframe.pack(fill='x')
        left_btns = ttk.Frame(btnframe)
        left_btns.pack(side='left')
        ttk.Button(left_btns, text="Ouvrir l'interface web", command=lambda: webbrowser.open(f'http://{self.ip}:5000/files')).pack(side='left', padx=(0,6))
        ttk.Button(left_btns, text="Uploader un fichier", command=self._on_upload_file_flask).pack(side='left', padx=(0,6))
        right_btns = ttk.Frame(btnframe)
        right_btns.pack(side='right')
        self.flask_start = ttk.Button(right_btns, text='Démarrer le serveur Web', command=self._on_start_flask)
        self.flask_stop = ttk.Button(right_btns, text='Arrêter le serveur Web', command=self._on_stop_flask)
        self.flask_start.pack(side='left', padx=(6,0))
        self.flask_stop.pack(side='left')
        sub_nb = ttk.Notebook(parent)
        sub_nb.pack(fill='both', expand=True, padx=8, pady=8)
        self.cloud_files_tab = ttk.Frame(sub_nb)
        self.flask_users_tab = ttk.Frame(sub_nb)
        self.flask_downloads_tab = ttk.Frame(sub_nb)
        sub_nb.add(self.cloud_files_tab, text='Fichiers')
        sub_nb.add(self.flask_users_tab, text='Utilisateurs connectés')
        sub_nb.add(self.flask_downloads_tab, text='Historique téléchargements')
        files_frame = ttk.Labelframe(self.cloud_files_tab, text='Fichiers disponibles', padding=8)
        files_frame.pack(fill='both', expand=True, padx=8, pady=8)
        self.cloud_files_container = files_frame
        self._refresh_cloud_files()
        users_frame = ttk.Labelframe(self.flask_users_tab, text='Utilisateurs connectés (temps réel)', padding=8)
        users_frame.pack(fill='both', expand=True, padx=8, pady=8)
        self.flask_users_list = tk.Listbox(users_frame, height=8)
        self.flask_users_list.pack(fill='both', expand=True)
        ttk.Button(users_frame, text='Rafraîchir', command=self._refresh_flask_users).pack(pady=4)
        downloads_frame = ttk.Labelframe(self.flask_downloads_tab, text='Historique des téléchargements', padding=8)
        downloads_frame.pack(fill='both', expand=True, padx=8, pady=8)
        self.flask_downloads_list = tk.Text(downloads_frame, height=10, state='disabled')
        self.flask_downloads_list.pack(fill='both', expand=True)
        ttk.Button(downloads_frame, text='Rafraîchir', command=self._refresh_flask_downloads).pack(pady=4)

    def _refresh_flask_users(self):
        # Cette fonctionnalité nécessite une route /api/connected_users côté Flask si souhaitée
        self.flask_users_list.delete(0, 'end')
        self.flask_users_list.insert('end', 'Non implémenté dans cette version')

    def _refresh_flask_downloads(self):
        import requests
        try:
            res = requests.get(f'http://{self.ip}:5000/api/download_history', timeout=5)
            history = res.json().get('history', [])
        except Exception:
            history = ['Erreur de connexion']
        self.flask_downloads_list.config(state='normal')
        self.flask_downloads_list.delete('1.0', 'end')
        for entry in history:
            self.flask_downloads_list.insert('end', entry + '\n')
        self.flask_downloads_list.config(state='disabled')

    def _refresh_cloud_files(self):
        for widget in self.cloud_files_container.winfo_children():
            widget.destroy()
        upload_dir = HERE / 'web_uploads'
        files = list(upload_dir.glob('*'))
        if not files:
            ttk.Label(self.cloud_files_container, text='Aucun fichier disponible.').pack(anchor='w')
            return
        for f in files:
            row = ttk.Frame(self.cloud_files_container)
            row.pack(fill='x', pady=2, padx=2)
            name = f.name
            size = f.stat().st_size // 1024
            mtime = time.strftime('%d/%m/%Y %H:%M', time.localtime(f.stat().st_mtime))
            ttk.Label(row, text=name, width=32).pack(side='left')
            ttk.Label(row, text=f'{size} Ko', width=10).pack(side='left')
            ttk.Label(row, text=mtime, width=18).pack(side='left')
            ttk.Button(row, text='Télécharger', command=lambda n=name: self._download_flask_file(n)).pack(side='left', padx=2)
            ttk.Button(row, text='Supprimer', command=lambda n=name: self._delete_flask_file(n)).pack(side='left', padx=2)
            ttk.Button(row, text='Copier lien', command=lambda n=name: self._copy_flask_file_link(n)).pack(side='left', padx=2)

    def _download_flask_file(self, filename):
        import requests
        save_path = filedialog.asksaveasfilename(title='Enregistrer sous', initialfile=filename)
        if not save_path:
            return
        url = f'http://{self.ip}:5000/files/{filename}'
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            messagebox.showinfo('Téléchargement', f'Fichier téléchargé : {save_path}')
        except Exception as e:
            messagebox.showerror('Erreur', f'Erreur lors du téléchargement : {e}')

    def _delete_flask_file(self, filename):
        import requests
        if not messagebox.askyesno('Confirmation', f'Supprimer le fichier {filename} ?'):
            return
        url = f'http://{self.ip}:5000/delete/{filename}'
        try:
            response = requests.post(url, timeout=10)
            if response.ok:
                self._refresh_cloud_files()
                messagebox.showinfo('Suppression', f'Fichier supprimé : {filename}')
            else:
                messagebox.showerror('Erreur', f'Suppression côté serveur échouée : {response.text}')
        except Exception as e:
            messagebox.showerror('Erreur', f'Erreur lors de la suppression : {e}')

    def _copy_flask_file_link(self, filename):
        url = f'http://{self.ip}:5000/files/{filename}'
        self.master.clipboard_clear()
        self.master.clipboard_append(url)
        messagebox.showinfo('Lien copié', f'Lien copié dans le presse-papiers :\n{url}')

    def _on_upload_file_flask(self):
        from tkinter import filedialog, messagebox
        import requests
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier à uploader")
        if not file_path:
            return
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                url = f'http://{self.ip}:5000/files'
                response = requests.post(url, files=files, timeout=20)
            if response.ok:
                messagebox.showinfo('Succès', 'Fichier uploadé avec succès !')
                self._refresh_cloud_files()
            else:
                messagebox.showerror('Erreur', f"Erreur lors de l'upload : {response.text}")
        except Exception as e:
            messagebox.showerror('Erreur', f"Erreur lors de l'upload : {e}")

    def update_global_status(self):
        if flask_process and flask_process.poll() is None:
            txt = 'Serveur Web démarré'
            color = '#28a745'
        else:
            txt = 'Serveur Web arrêté'
            color = '#dc3545'
        self.global_statusbar.config(text=txt, foreground=color)

    def update_buttons(self):
        if flask_process and flask_process.poll() is None:
            self.flask_start.state(['disabled'])
            self.flask_stop.state(['!disabled'])
            self.flask_status.config(text='Démarré', foreground='#28a745')
        else:
            self.flask_start.state(['!disabled'])
            self.flask_stop.state(['disabled'])
            self.flask_status.config(text='Arrêté', foreground='#dc3545')
        self.update_global_status()

    def on_close(self):
        if messagebox.askyesno('Confirmation', 'Voulez-vous vraiment quitter et arrêter le serveur web ?'):
            stop_flask()
            self.master.destroy()

    def _on_start_flask(self):
        threading.Thread(target=start_flask, args=(self._set_status,), daemon=True).start()
        self.after(800, self.update_buttons)

    def _on_stop_flask(self):
        threading.Thread(target=stop_flask, args=(self._set_status,), daemon=True).start()
        self.after(800, self.update_buttons)

    def _set_status(self, text, target=None):
        self.global_statusbar.config(text=text)
        self.update_global_status()

# ---------- Entrypoint ----------
def main():
    root = tk.Tk()
    root.title('Metadidomi Server Plus (Version simplifiée)')
    # Changement de l'icône de la barre des tâches sous Windows
    try:
        import ctypes
        app_id = u"Metadidomi.ServerPlus.Simplifiee"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass
    try:
        icon_path = str(HERE / 'app' / 'favicon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass
    window_width = 1000
    window_height = 520
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    root.minsize(380, 520)
    app = LauncherUI(root)
    app.pack(fill='both', expand=True)
    def _tick():
        app.update_buttons()
        app.after(2000, _tick)
    _tick()
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == '__main__':
    main()
