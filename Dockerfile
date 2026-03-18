FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    ffmpeg \
    aria2 \
    ca-certificates \
    wget \
    gnupg \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy project
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create downloads folder
RUN mkdir -p /app/downloads

CMD ["python", "main.py"]
