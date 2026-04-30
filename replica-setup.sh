until pg_isready -h pg-primary -p 5432 -U postgres; do
    echo "Waiting for primary database to be ready..."
    sleep 2
done

rm -rf /var/lib/postgresql/data/*
pg_basebackup -h pg-primary -D /var/lib/postgresql/data -U replicator -v -R -X stream

exec docker-entrypoint.sh postgres