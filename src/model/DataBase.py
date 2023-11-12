import sqlite3

class DataBase:
	def __init__(self, database):
		self.db = database

	def query(self, q):
		con = sqlite3.connect(self.db)
		cur = con.cursor()

		try:
			cur.execute(q)
			# Save (commit) the changes
			con.commit()
		except Exception as e:
			con.close()
			raise e
		# We can also close the connection if we are done with it.
		# Just be sure any changes have been committed or they will be lost.
		con.close()

	def multiQuery(self, q):
		con = sqlite3.connect(self.db)
		cur = con.cursor()

		cur.executescript(q)
		# Save (commit) the changes
		con.commit()

		# We can also close the connection if we are done with it.
		# Just be sure any changes have been committed or they will be lost.
		con.close()

	def getRows(self, q):
		con = sqlite3.connect(self.db)
		cur = con.cursor()
		cur.execute(q)
		datos = cur.fetchall()
		con.commit()
		con.close()
		return datos

	def get_column_names(self, table_name):
		result = self.getInfo(table_name)
		column_names = [row[1] for row in result]
		return column_names

	def exists(self, sql):
		con = sqlite3.connect(self.db)
		cur = con.cursor()
		cur.execute(sql)
		resultado = cur.fetchone()
		con.close()
		return True if resultado else False

	def getInfo(self, table_name):
		con = sqlite3.connect(self.db)
		cur = con.cursor()
		query = f"PRAGMA table_info({table_name});"
		cur.execute(query)
		result = cur.fetchall()
		con.close()
		return result