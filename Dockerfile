FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libsqlite3-dev \
    build-essential \
    openssh-server \
    munge \
    && rm -rf /var/lib/apt/lists/*

# Install DIAMOND BLASTP - if using srun, this must be on the host machine to run BLAST jobs
RUN wget https://github.com/bbuchfink/diamond/releases/download/v2.0.14/diamond-linux64.tar.gz \
    && tar xzf diamond-linux64.tar.gz \
    && mv diamond /usr/local/bin/ \
    && rm diamond-linux64.tar.gz

WORKDIR /npdc_portal

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Slurm user
RUN addgroup --gid 2016 slurm
RUN adduser --uid 1006 --gid 2016 --comment "SLURM User" --home /nonexistent --no-create-home --disabled-password --shell /bin/false slurm

COPY . .

CMD ["bash", "./startup.sh"]