import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy import stats
import numpy as np
from adjustText import adjust_text


LATEST_CPI_U = 251.001


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
		SELECT
			sum(salaries.salary),
			salaries.teamID,  -- internal team ID (not always the frandhise IDs)
			salaries.yearID,  -- year for this datapoint
			( CAST(teams.W AS FLOAT) / (teams.W+teams.L) ),  --- win %
			teams.franchID,  --- the generally known franchise ID
			round( ( sum(salaries.salary) * {0} ) / (SELECT i.value FROM inflation i WHERE i.year = salaries.yearID), 2 )  --- inflation adjusted salary sum
		FROM salaries
		JOIN teams ON teams.teamID = salaries.teamID AND teams.yearID = salaries.yearID
		WHERE salaries.teamID in ({1}) and salaries.yearID in ({2}) and salaries.salary is NOT NULL
		GROUP BY salaries.teamID, salaries.yearID;
		""".format(LATEST_CPI_U, _list_to_query_string(teams), _list_to_query_string(years)))
	rows = cur.fetchall()
	return rows


def generate_color_list(count):
	color_list = [
		'#e6194B',
		'#3cb44b',
		'#ffe119',
		'#4363d8',
		'#f58231',
		'#911eb4',
		'#42d4f4',
		'#f032e6',
		'#bfef45',
		'#fabebe',
		'#469990',
		'#e6beff',
		'#9A6324',
		'#fffac8',
		'#800000',
		'#aaffc3',
		'#808000',
		'#ffd8b1',
		'#000075',
		'#a9a9a9',
		'#ffffff',
		'#000000'
	]
	return color_list


def graph_pcts_over_years(database_rows_list, years):
	fig, ax = plt.subplots()
	fig.set_size_inches(18, 9)
	colors = generate_color_list(len(database_rows_list))

	for result in range(0, len(database_rows_list)):
		percentages = [row[3] for row in database_rows_list[result]]
		# salaries = [row[0] for row in database_rows_list[result]]
		adjusted_salaries = [row[5] for row in database_rows_list[result]]
		labels = ["{0} ({1})".format(row[4], row[2]) for row in database_rows_list[result]]
		for i in range(0, len(labels)):
			# ax.scatter(
			# 	salaries[i],
			# 	percentages[i],
			# 	c=colors[result],
			# 	s=8,
			# 	alpha=0.35
			# )
			ax.scatter(
				adjusted_salaries[i],
				percentages[i],
				c=colors[result],
				s=8,
				alpha=0.5
			)
		# print("MAX", max(salaries), 'MIN', min(salaries), 'YEARS', years[result])
		print("MAX (adjusted)", max(adjusted_salaries), 'MIN (adjusted)', min(adjusted_salaries), 'YEARS', years[result])
		ax.scatter(  # graph mean
			sum(adjusted_salaries) / float(len(adjusted_salaries)),
			sum(percentages) / float(len(percentages)),
			c=colors[result],
			s=30,
			alpha=1
		)

		# texts = [ax.text(salaries[i], percentages[i], labels[i], color='grey', fontsize=6) for i in range(len(labels))]

		gradient, intercept, r_value, p_value, std_err = stats.linregress(adjusted_salaries, percentages)
		mn = np.min(adjusted_salaries)
		mx = np.max(adjusted_salaries)
		x1 = np.linspace(mn, mx, 500)
		print('\t'.join([str(years[result]), str(r_value), str(gradient), str(intercept)]))   # output regression info
		# print("{0} ({1}):\t{2}x + {3}".format(years[result], r_value, gradient, intercept))   # output regression equation
		y1 = gradient * x1 + intercept
		plt.plot(x1, y1, c=colors[result], label='{0} - {1} (r={2})'.format(min(years[result]), max(years[result]), round(r_value, 4)))


	fmt = '${x:,.0f}'
	tick = mtick.StrMethodFormatter(fmt)
	ax.xaxis.set_major_formatter(tick)

	plt.xlim(left=0)
	plt.legend(loc='lower right')
	master_range = get_master_range_from_list(years)
	plt.title("Baseball Team Expenditures vs. Win % {0}-{1} (Adjused for Inflation to 2018 Values)".format(min(master_range), max(master_range)), fontdict={'fontsize': 18})
	plt.ylabel("Preseason Win %", style='italic')
	plt.xlabel("Annual Expenditure ($)", style='italic')
	plt.show()


def get_master_range_from_list(ranges_list):
	master_max = max(ranges_list[0])
	master_min = min(ranges_list[0])
	for r in ranges_list[1:]:
		if min(r) < master_min:
			master_min = min(r)
		if max(r) > master_max:
			master_max = max(r)
	return range(master_min, master_max + 1)


def main():
	database = "C:\\Users\\werdn\\Documents\\MLB-math-IA\\lahman-imported.db"
	database_ranges = [
		# range(1980, 1985),
		range(1985, 1990),
		range(1990, 1995),
		range(1995, 2000),
		range(2000, 2005),
		range(2005, 2010),
		range(2010, 2017)
	]

	# create a database connection
	conn = create_connection(database)
	results = []
	teams = get_teams_list(conn)
	for years in database_ranges:
		results.append(get_annual_salary_and_record(conn, teams, years))

	# get list of results
	results_count = 0
	for year_range_records in results:
		results_count += len(year_range_records)

	print(results_count, 'rows used...')
	graph_pcts_over_years(results, database_ranges)


if __name__ == '__main__':
	main()
