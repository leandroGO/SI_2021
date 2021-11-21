create_env:
	virtualenv -p python3 si1pyenv

install:
	pip3 install Flask SQLAlchemy Flask-SQLAlchemy SQLAlchemy-Utils \
	psycopg2 itsdangerous Flask-Session pymongo

create_db:
	@echo drop db...
	dropdb si1 -U alumnodb
	@echo create db...
	createdb si1 -U alumnodb
	@echo load db...
	gunzip -c dump_v1.5-P3.sql.gz | psql si1 -U alumnodb
