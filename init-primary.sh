set -e
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
    CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password';
    SELECT pg_create_physical_replication_slot('replica_1_slot);
EOSQL
echo "host eplication replicator 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"