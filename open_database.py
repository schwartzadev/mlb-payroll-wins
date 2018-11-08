import sqlite3
from sqlite3 import Error

def create_connection(db_file):
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)

	return None


def get_teams_list(connection):
	cur = connection.cursor()
	cur.execute("SELECT DISTINCT teamID from teams")
	rows = cur.fetchall()
	print(rows)


def get_team_record(connection, team, year):
	cur = connection.cursor()
	cur.execute("SELECT ( CAST(W AS FLOAT) / (W+L)), W, L from teams where teamID is '{0}' and yearID is '{1}'".format(team, year))
	rows = cur.fetchall()
	print(rows)


def get_annual_salary(connection, team, year):
	cur = connection.cursor()
	cur.execute("SELECT sum(salary) from salaries where teamID is '{0}' and yearID is '{1}'".format(team, year))
	rows = cur.fetchall()
	print(rows)



def main():
	database = "C:\\Users\\werdn\\Documents\\MLB-math-IA\\lahman-imported.db"

	# create a database connection
	conn = create_connection(database)
	# get_annual_salary(conn, 'WAS', 2005)
	# get_teams_list(conn)
	get_team_record(conn, 'COL', 2008)

if __name__ == '__main__':
	main()
