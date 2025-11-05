import sqlite3

def init_db():
    conn = sqlite3.connect('rps_bot.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            user_id INTEGER PRIMARY KEY,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            ties INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_score(user_id):
    conn = sqlite3.connect('rps_bot.db')
    c = conn.cursor()
    c.execute("SELECT wins, losses, ties FROM scores WHERE user_id = ?", (user_id,))
    score = c.fetchone()
    conn.close()
    if score:
        return score
    return 0, 0, 0

def update_score(user_id, result):
    conn = sqlite3.connect('rps_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO scores (user_id) VALUES (?)", (user_id,))
    if result == 'win':
        c.execute("UPDATE scores SET wins = wins + 1 WHERE user_id = ?", (user_id,))
    elif result == 'loss':
        c.execute("UPDATE scores SET losses = losses + 1 WHERE user_id = ?", (user_id,))
    elif result == 'tie':
        c.execute("UPDATE scores SET ties = ties + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
