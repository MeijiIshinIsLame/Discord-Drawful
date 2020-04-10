import sqlite3
import discord

PROMPT_DATABASE = 'prompt_database.db'
MAX_CHAR = 255
ROW_LIMIT = 4000

def get_random_prompt(table_name="defaultprompts"):
	conn = conn = sqlite3.connect(PROMPT_DATABASE)
	rows = execute_sql_selectall(conn, "SELECT prompt FROM %s ORDER BY RANDOM() LIMIT 1" % (table_name,))
	return rows[0][0]

def execute_sql_selectall(conn, sql):
	cur = conn.cursor()
	cur.execute(sql)
	rows = cur.fetchall()
	return rows

def create_default_db():
	prompts = ["a donkey", "idk man draw anything", "kill me dawg", "urushi? idk", "mfer"]

	conn = conn = sqlite3.connect(PROMPT_DATABASE)
	cur = conn.cursor()
	sql = "CREATE TABLE IF NOT EXISTS defaultprompts (id integer, prompt text, serverid text)"
	cur.execute(sql)

	entryid = 0
	serverid = "default"

	for prompt in prompts:
		values = (entryid, prompt, serverid)
		sql = "INSERT INTO defaultprompts (id, prompt, serverid) VALUES (?, ?, ?)"
		cur.execute(sql, values)
		entryid += 1

	conn.commit()
	conn.close()