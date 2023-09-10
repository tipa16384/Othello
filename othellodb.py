import sqlite3
import json
import os

MOVE_DB = 'othello.db'
DB_CONNECTION = None

def get_move_db():
    global DB_CONNECTION
    if not DB_CONNECTION:
        db_created = os.path.exists(MOVE_DB)
        DB_CONNECTION = sqlite3.connect(MOVE_DB)
        cur = DB_CONNECTION.cursor()
        if not db_created:
            cur.execute("CREATE TABLE moves(notation, moves)")
    return DB_CONNECTION

def get_valid_moves_from_db(notation):
    conn = get_move_db()
    cur = conn.cursor()
    cur.execute("SELECT moves FROM moves WHERE notation=?", (notation,))
    row = cur.fetchone()
    if row:
        return json.loads(row[0])
    else:
        return None

def write_valid_moves_to_db(notation, valid_moves):
    conn = get_move_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO moves VALUES (?, ?)", (notation, json.dumps(valid_moves)))
    conn.commit()
