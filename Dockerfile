FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libsqlite3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install DIAMOND BLASTP
RUN wget https://github.com/bbuchfink/diamond/releases/download/v2.0.14/diamond-linux64.tar.gz \
    && tar xzf diamond-linux64.tar.gz \
    && mv diamond /usr/local/bin/ \
    && rm diamond-linux64.tar.gz

WORKDIR /npdc_portal

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "./startup.sh"]