FROM postgres:16

WORKDIR /app
# Install system dependencies for Posgres
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r --break-system-packages requirements.txt


# Copy your configs and code
COPY core/db/configs/postgresql.conf /etc/postgresql/postgresql.conf
COPY core/db/configs/pg_hba.conf /etc/postgresql/pg_hba.conf


# Copy the rest of the code
COPY . .


