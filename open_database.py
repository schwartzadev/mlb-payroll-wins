import sqlite3
from sqlite3 import Error

def create_connection(db_file):
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)

	return None


def get_annual_salary(connection, team, year):
	cur = connection.cursor()
	cur.execute("SELECT sum(salary) from salaries where teamID is '{0}' and yearID is '{1}'".format(team, year))
	rows = cur.fetchall()
	print(rows)



def main():
	database = "C:\\Users\\werdn\\Documents\\MLB-math-IA\\lahman-imported.db"

	# create a database connection
	conn = create_connection(database)
	get_annual_salary(conn, 'WAS', 2005)

if __name__ == '__main__':
	main()
