from bottle import route, run, auth_basic
import os
import subprocess

BASIC_AUTH_USER = os.environ["BASIC_AUTH_USER"]
BASIC_AUTH_PASSWORD = os.environ["BASIC_AUTH_PASSWORD"]
LOG_DIR = os.environ.get("LOG_DIR", "/logs")


def is_authenticated(user, password):
    """Basic authentication function for Bottle."""
    return user == BASIC_AUTH_USER and password == BASIC_AUTH_PASSWORD


def list_hosts() -> list[str]:
    return []  # TODO


@route("/")
@auth_basic(is_authenticated)
def index():
    hosts = list_hosts()

    if len(hosts) == 0:
        return "No hosts found in logs."

    return "<br>".join(f"<a href='/view/{host}'>{host}</a>" for host in hosts)


@route("/view/<host>")
@auth_basic(is_authenticated)
def render_goaccess_for_host(host: str):
    filter_str = f'"host":"{host}"'

    result = subprocess.run(
        [
            "sh",
            "-c",
            f"zgrep -hF '{filter_str}' -- {LOG_DIR}/*.log {LOG_DIR}/*.log.gz | goaccess --log-format=CADDY --output html -",
        ],
        stdout=subprocess.PIPE,
        check=True,
    )

    return result.stdout.decode("utf-8")


def main():
    run(host="0.0.0.0", port=4876)


if __name__ == "__main__":
    main()
