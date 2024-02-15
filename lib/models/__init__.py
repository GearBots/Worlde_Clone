import sqlite3

CONN = sqlite3.connect('wordle.db')
CURSOR = CONN.cursor()
