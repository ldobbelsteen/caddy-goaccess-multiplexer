FROM docker.io/python:3.13-bookworm
STOPSIGNAL SIGINT
RUN apt update && apt install -y goaccess && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 4876
CMD ["python", "app.py"]
