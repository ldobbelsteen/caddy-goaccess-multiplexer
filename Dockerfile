# Take official Alpine-based GoAccess image as source of the binary.
FROM docker.io/allinurl/goaccess:latest as goaccess

# Use a Python base for our image.
FROM docker.io/python:3.13-alpine

# Install the same dependencies as the GoAccess image (see https://github.com/allinurl/goaccess/blob/master/Dockerfile).
RUN apk add --no-cache \
    gettext-libs \
    libmaxminddb \
    ncurses-libs \
    openssl \
    tzdata

# Copy the GoAccess binary from the previous stage.
COPY --from=goaccess /usr/bin/goaccess /usr/bin/goaccess
COPY --from=goaccess /usr/share /usr/share
COPY --from=goaccess /usr/share/zoneinfo /usr/share/zoneinfo

# Install Python dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy and run the application code.
COPY app.py .
STOPSIGNAL SIGINT
EXPOSE 4876
CMD ["python", "app.py"]
