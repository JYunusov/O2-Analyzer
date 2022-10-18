CREATE TABLE IF NOT EXISTS plots (
	id integer NOT NULL,
	plot_guid varchar(80) NOT NULL,
	plot_timestamp timestamp NOT NULL,
	plot_oxygen real NOT NULL,
	plot_temp real NOT NULL,
	PRIMARY KEY(id AUTOINCREMENT)
);