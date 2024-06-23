import sqlite3
from datetime import datetime

def create_table():
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS birthdays (
        user_id TEXT,
        name TEXT,
        month INTEGER,
        day INTEGER,
        PRIMARY KEY (user_id, name)
    );
    ''')
    conn.commit()
    conn.close()

def add_birthday(user_id, name, month, day):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO birthdays (user_id, name, month, day) VALUES (?, ?, ?, ?)
    ''', (user_id, name, month, day))
    conn.commit()
    conn.close()

def get_birthday(user_id, name=None):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    if user_id:
        cursor.execute('''
        SELECT month, day FROM birthdays WHERE user_id = ?
        ''', (user_id,))
    else:
        cursor.execute('''
        SELECT month, day FROM birthdays WHERE name = ?
        ''', (name,))
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def delete_birthday(user_id, name=None):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    if user_id:
        cursor.execute('''
        DELETE FROM birthdays WHERE user_id = ?
        ''', (user_id,))
    else:
        cursor.execute('''
        DELETE FROM birthdays WHERE name = ?
        ''', (name,))
    conn.commit()
    conn.close()

def get_all_birthdays():
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, month, day FROM birthdays')
    results = cursor.fetchall()
    conn.close()

    birthdays = {}
    for row in results:
        user_id, name, month, day = row
        birthdays[user_id] = (name, month, day)

    return birthdays

def get_birthdays_today():
    today = datetime.now()
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT user_id, name FROM birthdays WHERE month = ? AND day = ?
    ''', (today.month, today.day))
    result = cursor.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in result]

def get_birthdays_by_date(month, day):
    conn = sqlite3.connect('birthdays.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT user_id, name FROM birthdays WHERE month = ? AND day = ?
    ''', (month, day))
    result = cursor.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in result]


create_table()