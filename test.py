import os
from db import create_plot
import uuid
import datetime
import sys
import sqlite3
from sqlite3 import Error

a = {
  'plot_guid': uuid.uuid4(),
  'plot_timestamp': datetime.datetime.now(),
  'plot_oxygen': 20.93,
  'plot_temp': 26.5
}

create_plot(a)
print(a)
sys.exit()

BASEDIR = os.getcwd() + "/"
database = BASEDIR + 'plots.db'

conn = sqlite3.connect(database)

a = {
    'plot_guid': str(uuid.uuid4()),
    'plot_times': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'plot_oxygen': 24.54,
    'plot_temp': 39.2
}
print(a)
print(a['plot_temp'])
sys.exit()

sql = f"INSERT INTO plots (plot_guid, plot_timestamp, plot_oxygen, plot_temp) VALUES ('{a[0]}', '{a[1]}', {a[2]}, {a[3]});"
print(sql)
sys.exit()


# c = conn.cursor()
# c .execute(sql)
# conn.commit()
# SELECT * FROM plots;
# """

# print(sql)
sys.exit()

# conn = create_connection()
# create_table(conn)



# DROP TABLE plots;

# CREATE TABLE IF NOT EXISTS plots 
# (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, 
#  plot_guid varchar(80) NOT NULL, 
#  plot_timestamp timestamp(128) NOT NULL, 
#  plot_result real(128) NOT NULL);

# INSERT INTO plots (plot_guid, plot_timestamp, plot_result) 
# VALUES ('asdf', '03/15/21 21:56:28', 64.4321);

# select * from plots;