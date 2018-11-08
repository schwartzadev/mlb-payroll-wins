import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from adjustText import adjust_text


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
	teams = [r[0] for r in rows]
	return teams


def get_team_record(connection, team, year):
	cur = connection.cursor()
	cur.execute("SELECT ( CAST(W AS FLOAT) / (W+L) ), W, L from teams where teamID is '{0}' and yearID is '{1}'".format(team, year))
	rows = cur.fetchall()
	print(rows)


def _list_to_query_string(data):
	data = ["'"+str(y)+"'" for y in data]
	data_string = ', '.join(data)
	return data_string


def get_annual_salary_and_record(connection, teams, years):
	cur = connection.cursor()
	cur.execute("""
		SELECT sum(salaries.salary), salaries.teamID, salaries.yearID, ( CAST(teams.W AS FLOAT) / (teams.W+teams.L) ), teams.W, teams.L
		FROM salaries
		JOIN teams ON teams.teamID = salaries.teamID AND teams.yearID = salaries.yearID
		WHERE salaries.teamID in ({0}) and salaries.yearID in ({1})
		GROUP BY salaries.teamID, salaries.yearID;
		""".format(_list_to_query_string(teams), _list_to_query_string(years)))
		# WHERE salaries.teamID in ('ATL', 'BAL') and salaries.yearID in ({1})   # for multiple teams
	rows = cur.fetchall()
	return rows


def graph_pcts_over_years(database_rows, years):
	fig, ax = plt.subplots()
	fig.set_size_inches(18, 9)
	percentages = [row[3] for row in database_rows]
	salaries = [row[0] for row in database_rows]
	labels = ["{0} ({1})".format(row[1], row[2]) for row in database_rows]

	for i in range(0, len(labels)):
		ax.scatter(
			salaries[i],
			percentages[i],
			c='r',
			s=5
		)
	texts = [ax.text(salaries[i], percentages[i], labels[i], color='grey', fontsize=6) for i in range(len(labels))]

	gradient, intercept, r_value, p_value, std_err = stats.linregress(salaries, percentages)
	mn = np.min(salaries)
	mx = np.max(salaries)
	x1 = np.linspace(mn, mx, 500)
	y1 = gradient * x1 + intercept
	plt.plot(x1, y1, c='b')


	plt.legend(loc='upper left')
	plt.title("Baseball Team Expenditures vs. Win % ({0}-{1})".format(min(years), max(years)))
	plt.ylabel("Preseason Win %")
	plt.xlabel("Annual Expenditure ($)")
	plt.show()


def main():
	database = "C:\\Users\\werdn\\Documents\\MLB-math-IA\\lahman-imported.db"

	# create a database connection
	conn = create_connection(database)
	# teams = ['BOS', 'COL']
	teams = get_teams_list(conn)
	years = range(1980, 2017)
	results = get_annual_salary_and_record(conn, teams, years)
	print(len(results), 'rows used...')
	graph_pcts_over_years(results, years)


if __name__ == '__main__':
	main()
