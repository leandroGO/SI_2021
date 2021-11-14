create_env:
	virtualenv -p python3 si1pyenv
	source si1pyenv/bin/activate
	pip3 install Flask SQLAlchemy Flask-SQLAlchemy SQLAlchemy-Utils \
	psycopg2 itsdangerous Flask-Session

create_db:
	@echo drop db...
	dropdb si1 -U alumnodb
	@echo create db...
	createdb si1 -U alumnodb
	@echo load db...
	gunzip -c dump_v1.4.sql.gz | psql si1 -U alumnodb

run_actualiza:
	cat SQL/actualiza.sql | psql si1 -U alumnodb

test:
	@echo es un test
