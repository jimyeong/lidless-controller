
```
source venv/bin/activate

FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY core/db/configs/postgresql.conf /etc/postgresql/postgresql.conf
COPY core/db/configs/pg_hba.conf /etc/postgresql/pg_hba.conf
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]


# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Start the server on the port Railway provides
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

```