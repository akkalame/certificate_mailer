from kernel import _dict
class DBTable:
	def __init__(self, db, table=""):
		self.table = table
		self.db = db
		self.info = _dict()
		self._LoadInfo()

	def _LoadInfo(self):
		result = self.db.getInfo(self.table)
		for r in result:
			self.info[r[1]] = r[2]


	def _Crear(self, db, data):
		columns = "("
		for column in data:
			if columns != "(": columns += ", "
			columns += column
		columns += ")"

		values = "("
		for column in data:
			if values != "(": values += ", "
			values += "'{0}'".format(data[column])
		values += ")"

		q = """
			INSERT INTO {0} 
			{1} 
			VALUES{2}
		""".format(self.table, columns, values)

		try:
			db.query(q)
			return 'REGISTRO_INSERTADO'
		except Exception as e:
			return 'REGISTRO_NO_INSERTADO'

	def _Listar(self, db=None, columns="*", filters={}):
		if not db: db = self.db
		fields = columns
		if type(columns) == list: fields = ", ".join(columns)

		cond = get_filters_str(filters)
		if cond != "":
			cond = "WHERE "+ cond

		sql = "SELECT {1} FROM {0} {2}".format(self.table, fields, cond)
		
		rows = db.getRows(sql)
		return self._Data2Dict(db, rows, columns)


	def _Exists(self, db, filters={}):
		if type(filters) == dict: filters = _dict(filters)
		if not filters: return

		cond = get_filters_str(filters)

		sql = "SELECT * FROM {0} WHERE {1}".format(self.table, cond)

		# Ejecutar la consulta
		return db.exists(sql)

	def _Actualizar(self, db, data, filters):
		cond = get_filters_str(filters)
		dataSet = ""
		for column in data:
			if dataSet != "":
				dataSet += ", " 
			dataSet += "{0} = {1}".format(column, self._Value2DataType(column, data[column]))

		q = 'UPDATE {0} SET {1} WHERE {2}'.format(self.table, dataSet, cond)
		try:
			db.query(q)
			return 'REGISTRO_ACTUALIZADO'
		except Exception as e:
			return 'REGISTRO_NO_ACTUALIZADO'


	def _Eliminar(self, db, filters):
		cond = get_filters_str(filters)
		q = 'DELETE FROM {0} WHERE {1}'.format(self.table, cond)
		try:
			db.query(q)
			return 'REGISTRO_ELIMINADO'
		except:
			return 'REGISTRO_NO_ELIMINADO'

	def _Data2Dict(self, db, data, columns):
		# Obtener los nombres de las columnas de la tabla
		if columns == "*":
			columns = db.get_column_names(self.table)  # Reemplaza 'mail_server' con el nombre de tu tabla

		# Crear una lista de diccionarios donde cada diccionario representa una fila
		result = []
		for row in data:
			row_dict = _dict(zip(columns, row))
			result.append(row_dict)
		return result

	def _Value2DataType(self, column, value):
		if self.info[column] in ("INTEGER", "REAL", "NUMERIC"):
			return value
		else:
			return "'{0}'".format(value)

class TabMailServer(DBTable):
	def __init__(self, db):
		super().__init__(db, "mail_server")


class TabEmailAccount(DBTable):
	def __init__(self, db):
		super().__init__(db, "email_account")

class TabLanguage(DBTable):
	def __init__(self, db):
		super().__init__(db, "language")

class TabPreference(DBTable):
	def __init__(self, db):
		super().__init__(db, "preference")

def get_filters_str(filters):
	cond = ""
	for key in filters:
		if cond == "": 
			cond += "{0} = '{1}'".format(key, filters[key])
		else:
			cond += " and {0} = '{1}'".format(key, filters[key])
	return cond
		