import sqlite3

conn = sqlite3.connect('messages.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (date text, from_address text, message text)''')
conn.commit()
