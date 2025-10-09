import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent

def show_flask_db_view(parent):
    db_path = HERE / 'file_stats.db'
    win = tk.Toplevel(parent)
    win.title('Base de données file_stats.db')
    win.geometry('800x500')
    # Sélection de la table
    try:
        conn = sqlite3.connect(db_path)
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    except Exception as e:
        messagebox.showerror('Erreur', f'Impossible d’ouvrir la base : {e}')
        return
    table_var = tk.StringVar(value=tables[0] if tables else '')
    table_menu = ttk.OptionMenu(win, table_var, table_var.get(), *tables)
    table_menu.pack(pady=8)
    # Barre de recherche/filtre
    search_var = tk.StringVar()
    search_frame = ttk.Frame(win)
    search_frame.pack(fill='x', padx=8, pady=(2,0))
    ttk.Label(search_frame, text='Recherche :').pack(side='left')
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side='left', fill='x', expand=True, padx=(4,0))
    frame = ttk.Frame(win)
    frame.pack(fill='both', expand=True)
    tree = ttk.Treeview(frame, columns=[], show='headings')
    tree.pack(fill='both', expand=True, side='left')
    # Ajout scroll vertical et horizontal
    vscroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    vscroll.pack(side='right', fill='y')
    hscroll = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    hscroll.pack(side='bottom', fill='x')
    tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
    def refresh_table():
        table = table_var.get()
        cur = conn.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        tree['columns'] = cols
        tree.delete(*tree.get_children())
        for col in cols:
            tree.heading(col, text=col)
        try:
            query = search_var.get().strip()
            if query:
                # Filtre sur toutes les colonnes (LIKE)
                where = ' OR '.join([f"{col} LIKE ?" for col in cols])
                params = [f"%{query}%"] * len(cols)
                rows = conn.execute(f"SELECT * FROM {table} WHERE {where}", params).fetchall()
            else:
                rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            for row in rows:
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror('Erreur', f'Impossible d’afficher la table : {e}')
    def on_table_change(*a):
        refresh_table()
    table_var.trace_add('write', on_table_change)
    def on_search(*a):
        refresh_table()
    search_var.trace_add('write', on_search)
    refresh_table()
    # Suppression d’une ligne sélectionnée
    def delete_selected():
        sel = tree.selection()
        if not sel:
            return
        if not messagebox.askyesno('Confirmation', 'Supprimer la ligne sélectionnée ?'):
            return
        item = tree.item(sel[0])
        values = item['values']
        table = table_var.get()
        # Suppression par ID si possible
        try:
            cur = conn.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cur.fetchall()]
            if 'id' in cols:
                idx = cols.index('id')
                conn.execute(f"DELETE FROM {table} WHERE id=?", (values[idx],))
            else:
                # Suppression par toutes les valeurs (peu fiable)
                where = ' AND '.join([f"{col}=?" for col in cols])
                conn.execute(f"DELETE FROM {table} WHERE {where}", tuple(values))
            conn.commit()
            refresh_table()
        except Exception as e:
            messagebox.showerror('Erreur', f'Impossible de supprimer : {e}')
    # --- Barre d'outils ---
    toolbar = ttk.Frame(win)
    toolbar.pack(fill='x', pady=(4,0))
    def open_edit_window(mode):
        sel = tree.selection()
        if mode == 'edit' and not sel:
            messagebox.showinfo('Info', 'Sélectionnez une ligne à modifier.')
            return
        table = table_var.get()
        cur = conn.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        values = tree.item(sel[0])['values'] if mode == 'edit' else ['' for _ in cols]
        edit_win = tk.Toplevel(win)
        edit_win.title('Éditer la ligne' if mode=='edit' else 'Ajouter une ligne')
        entries = {}
        for i, col in enumerate(cols):
            ttk.Label(edit_win, text=col).grid(row=i, column=0, sticky='w', padx=8, pady=4)
            ent = ttk.Entry(edit_win)
            ent.grid(row=i, column=1, padx=8, pady=4)
            ent.insert(0, values[i] if i < len(values) else '')
            entries[col] = ent
        def save():
            vals = [entries[c].get() for c in cols]
            try:
                if mode == 'edit':
                    # Update par ID si possible
                    if 'id' in cols:
                        idx = cols.index('id')
                        conn.execute(f"UPDATE {table} SET " + ','.join([f"{c}=?" for c in cols if c!='id']) + f" WHERE id=?", [v for i,v in enumerate(vals) if cols[i]!='id'] + [vals[idx]])
                    else:
                        where = ' AND '.join([f"{c}=?" for c in cols])
                        conn.execute(f"UPDATE {table} SET " + ','.join([f"{c}=?" for c in cols]) + f" WHERE {where}", vals*2)
                else:
                    conn.execute(f"INSERT INTO {table} (" + ','.join(cols) + ") VALUES (" + ','.join(['?']*len(cols)) + ")", vals)
                conn.commit()
                refresh_table()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror('Erreur', f"Impossible d'enregistrer : {e}")
        ttk.Button(edit_win, text='Enregistrer', command=save).grid(row=len(cols), column=0, columnspan=2, pady=8)
    btn_add = ttk.Button(toolbar, text='Ajouter', command=lambda: open_edit_window('add'))
    btn_add.pack(side='left', padx=4)
    btn_edit = ttk.Button(toolbar, text='Modifier', command=lambda: open_edit_window('edit'))
    btn_edit.pack(side='left', padx=4)
    btn_del = ttk.Button(toolbar, text='Supprimer', command=delete_selected)
    btn_del.pack(side='left', padx=4)
    # Fermeture propre
    def on_close():
        try:
            conn.close()
        except Exception:
            pass
        win.destroy()
    win.protocol('WM_DELETE_WINDOW', on_close)
    win.grid_rowconfigure(2, weight=1)
    win.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    tree.pack(fill='both', expand=True, side='left')