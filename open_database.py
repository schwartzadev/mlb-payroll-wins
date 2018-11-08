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
	cur.execute("SELECT ( CAST(W AS FLOAT) / (W+L) ), W, L from teams where teamID is '{0}' and yearID is '{1}'".format(team, year))
	rows = cur.fetchall()
	print(rows)


def get_annual_salary_and_record(connection, team, year):
	cur = connection.cursor()
	cur.execute("""
		SELECT sum(salaries.salary), salaries.teamID, salaries.yearID, ( CAST(teams.W AS FLOAT) / (teams.W+teams.L) ), teams.W, teams.L
		FROM salaries
		JOIN teams ON teams.teamID = salaries.teamID AND teams.yearID = salaries.yearID
		WHERE salaries.teamID is '{0}' AND salaries.yearID is '{1}';
		""".format(team, year))
	rows = cur.fetchall()
	print(rows)



def main():
	database = "C:\\Users\\werdn\\Documents\\MLB-math-IA\\lahman-imported.db"

	# create a database connection
	conn = create_connection(database)
	team = 'COL'
	year = 2008
	get_annual_salary_and_record(conn, team, year)
	# get_teams_list(conns)
	get_team_record(conn, team, year)

if __name__ == '__main__':
	main()
