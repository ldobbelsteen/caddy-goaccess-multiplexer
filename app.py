from glob import glob
from bottle import route, run, auth_basic
import os
import subprocess
import gzip
import re
from cachetools import cached, TTLCache

BASIC_AUTH_USER = os.environ["BASIC_AUTH_USER"]
BASIC_AUTH_PASSWORD = os.environ["BASIC_AUTH_PASSWORD"]
LOG_DIR = os.environ.get("LOG_DIR", "/logs")
GEO_IP_DB_PATH = os.environ.get("GEO_IP_DB_PATH")


def is_authenticated(user, password):
    """Basic authentication function for Bottle."""
    return user == BASIC_AUTH_USER and password == BASIC_AUTH_PASSWORD


@cached(cache=TTLCache(maxsize=1, ttl=1800))
def list_hosts() -> set[str]:
    """List all unique hosts found in log files."""
    result = set()
    host_re = r'"host":"([^"]+)"'

    for file in glob(os.path.join(LOG_DIR, "*.log")):
        with open(file, "r") as f:
            for line in f:
                match = re.search(host_re, line)
                if match:
                    result.add(match.group(1))

    for file in glob(os.path.join(LOG_DIR, "*.log.gz")):
        with gzip.open(file, "rt") as f:
            for line in f:
                match = re.search(host_re, line)
                if match:
                    result.add(match.group(1))

    return result


@route("/")
@auth_basic(is_authenticated)
def index():
    """Index page listing all hosts found in logs."""
    hosts = list_hosts()

    if len(hosts) == 0:
        return "No hosts found in logs."

    sorted_hosts = sorted(hosts)
    sorted_hosts.insert(0, "All")

    return "<br>".join(f"<a href='/view/{host}'>{host}</a>" for host in sorted_hosts)


@route("/view/<host>")
@auth_basic(is_authenticated)
def render_goaccess_for_host(host: str):
    """Render GoAccess report for a specific host."""
    if host == "All":
        filter_str = ""
    else:
        filter_str = f'"host":"{host}"'

    command = [
        "sh",
        "-c",
        f"zgrep -hF '{filter_str}' -- {LOG_DIR}/*.log {LOG_DIR}/*.log.gz | goaccess --log-format=CADDY --output html",
    ]
    if GEO_IP_DB_PATH:
        command[-1] += f" --geoip-database {GEO_IP_DB_PATH}"
    command[-1] += " -"

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        check=True,
    )

    return result.stdout.decode("utf-8")


def main():
    run(host="0.0.0.0", port=4876)


if __name__ == "__main__":
    main()
