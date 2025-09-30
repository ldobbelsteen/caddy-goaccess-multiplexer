from bottle import route, run, auth_basic
import os
import subprocess

BASIC_AUTH_USER = os.environ["BASIC_AUTH_USER"]
BASIC_AUTH_PASSWORD = os.environ["BASIC_AUTH_PASSWORD"]
LOG_DIR = os.environ["LOG_DIR"]
GOACCESS_OPTIONS = os.environ["GOACCESS_OPTIONS"].split()


def is_authenticated(user, password):
    """Basic authentication function for Bottle."""
    return user == BASIC_AUTH_USER and password == BASIC_AUTH_PASSWORD


def list_hostnames() -> list[str]:
    return []  # TODO


@route("/")
@auth_basic(is_authenticated)
def index():
    hostnames = list_hostnames()

    if len(hostnames) == 0:
        return "No hostnames found in logs."

    return "<br>".join(
        f"<a href='/view/{hostname}'>{hostname}</a>" for hostname in hostnames
    )


@route("/view/<hostname>")
@auth_basic(is_authenticated)
def render_goaccess_for_hostname(hostname: str):
    filter_str = f'"host":"{hostname}"'

    result = subprocess.run(
        [
            "sh",
            "-c",
            f"zgrep -hF '{filter_str}' -- {LOG_DIR}/*.log {LOG_DIR}/*.log.gz | goaccess --log-format=CADDY --output html {' '.join(GOACCESS_OPTIONS)} -",
        ],
        stdout=subprocess.PIPE,
        check=True,
    )

    return result.stdout.decode("utf-8")


def main():
    run(host="0.0.0.0", port=4876)


if __name__ == "__main__":
    main()
