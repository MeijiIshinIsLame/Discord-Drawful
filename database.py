import sqlite3

PROMPT_DATABASE = 'prompt_database.db'
MAX_CHAR = 255
ROW_LIMIT = 4000

def get_random_prompt(table_name="defaultprompts"):
	conn = conn = sqlite3.connect(PROMPT_DATABASE)
	rows = execute_sql_selectall(conn, "SELECT prompt FROM %s ORDER BY RANDOM() LIMIT 1" % (table_name,))
	conn.close()
	return rows[0][0]

def get_db_count(table_name="defaultprompts"):
	conn = sqlite3.connect(PROMPT_DATABASE)
	cur = conn.cursor()
	cur.execute("SELECT MAX(id) FROM %s" % (table_name,))
	count = cur.fetchone()[0] + 1
	return int(count)

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

print(get_db_count())