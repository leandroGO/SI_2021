virtualenv -p python3 si1pyenv
source si1pyenv/bin/activate
pip3 install Flask SQLAlchemy==1.4 Flask-SQLAlchemy SQLAlchemy-Utils \
psycopg2 itsdangerous Flask-Session
