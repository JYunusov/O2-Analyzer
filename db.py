import sqlite3
from sqlite3 import Error
import os
import sys

BASEDIR = os.getcwd() + "/"
database = BASEDIR + 'plots.db'

def create_connection():
    # create a database connection to a SQLite database
    conn = None
    try:
        ### add later - check if database file exists
        ### if not, copy empty.db and name it plots.db

        conn = sqlite3.connect(database)

        print(conn)
        sys.exit()
        return conn
    except Error as e:
        print(e)
        sys.exit()

# this should be added later to init/re-init the db
# def create_table(conn):
#     try:
#         # create table if it doesn't exist
#         c = conn.cursor()
#         sql = """
# CREATE TABLE IF NOT EXISTS plots (
# 	id integer NOT NULL,
# 	plot_guid varchar(80) NOT NULL,
# 	plot_timestamp timestamp NOT NULL,
# 	plot_oxygen real NOT NULL,
# 	plot_temp real NOT NULL,
# 	PRIMARY KEY(id AUTOINCREMENT)
# );
# """
#         c.execute(sql)
#         conn.commit()
#     except Error as e:
#         print(e)
        


def create_plot(dict):
    # dict fields:
    # plot_guid - guid for test
    # plot_timestamp - datetime of plot
    # plot_oxygen - oxygen value
    # plot_temp - temperature value

    # add plot to database
    conn = create_connection()
    with conn:
        #create_table(conn)
        
        p = {
            'plot_guid': dict['plot_guid'],
            'plot_timestamp': dict['plot_timestamp'],
            'plot_oxygen': dict['plot_oxygen'],
            'plot_temp': dict['plot_temp']
        }

        c = conn.cursor()
        sql = f"INSERT INTO plots (plot_guid, plot_timestamp, plot_oxygen, plot_temp) VALUES ('{p['plot_guid']}', '{p['plot_timestamp']}', {p['plot_oxygen']}, {p['plot_temp']});"

        c.execute(sql)
        conn.commit()

def fetch_plots(conn):
    # query plots - not used except for debug right now
    # in the future, you will sync this data to an external resource
    with conn:
        c = conn.cursor()
        c.execute('SELECT * FROM plots WHERE guid = ?', guid)
        rows = cur.fetchall()

        for row in rows:
            print(row)


if __name__ == '__main__':
    print("run python GUI.py")
