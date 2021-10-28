sudo systemctl restart postgresql
dropdb si1 -U alumnodb
createdb si1 -U alumnodb
gunzip -c dump_v1.4.sql.gz | psql si1 -U alumnodb
