FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies (Added Audio Drivers & Pulseaudio)
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
    pulseaudio \
    libasound2 \
    alsa-utils \
    libpulse-dev \
    xvfb \
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

# --- IMPORTANT: PulseAudio Setup ---
# Ye line PulseAudio ko background mein chalne ke liye config karti hai
RUN mkdir -p /var/run/pulse /home/pulse && \
    chmod -R 777 /var/run/pulse /home/pulse

# Bot start karne se pehle PulseAudio start karenge
CMD pulseaudio -D --exit-idle-time=-1 && python main.py
