# 🚖 CAB 

Coronavirus Answering Bot 🚕

## Postgress SQL backup/restore

dump data: `docker exec -t your-db-container pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql`

restore data: `cat your_dump.sql | docker exec -i your-db-container psql -U postgres`

