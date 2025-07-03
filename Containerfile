FROM docker.io/python:3.13-bookworm

# Install the latest GoAccess version
RUN apt update && apt install -y wget gnupg lsb-release ca-certificates && rm -rf /var/lib/apt/lists/*
RUN wget -O - https://deb.goaccess.io/gnugpg.key | gpg --dearmor -o /usr/share/keyrings/goaccess.gpg && echo "deb [signed-by=/usr/share/keyrings/goaccess.gpg arch=$(dpkg --print-architecture)] https://deb.goaccess.io/ $(lsb_release -cs) main" >/etc/apt/sources.list.d/goaccess.list
RUN apt update && apt install -y goaccess && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY app.py .
STOPSIGNAL SIGINT
EXPOSE 4876

CMD ["python", "app.py"]
