FROM postgres:16

# 1. Install specific python3 packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Use 'pip3' and the break-system-packages override
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# 3. Rest of your config
COPY . .
COPY core/db/configs/postgresql.conf /etc/postgresql/postgresql.conf
COPY core/db/configs/pg_hba.conf /etc/postgresql/pg_hba.conf

# 4. CRITICAL: Fix permissions so the 'postgres' user can read the configs
RUN chown -R postgres:postgres /etc/postgresql/ /app/

# 5. Switch to the unprivileged user for the DB cards
USER postgres