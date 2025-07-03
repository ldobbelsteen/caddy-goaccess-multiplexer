from bottle import route, run, auth_basic
import os
import subprocess

BASIC_AUTH_USER = os.environ["BASIC_AUTH_USER"]
BASIC_AUTH_PASSWORD = os.environ["BASIC_AUTH_PASSWORD"]
LOG_DIR = os.environ["LOG_DIR"]
GOACCESS_OPTIONS = os.environ["GOACCESS_OPTIONS"].split()


def is_authenticated(user, password):
    return user == BASIC_AUTH_USER and password == BASIC_AUTH_PASSWORD


def list_log_subdirs():
    return [d for d in os.listdir(LOG_DIR) if os.path.isdir(os.path.join(LOG_DIR, d))]


@route("/")
@auth_basic(is_authenticated)
def index():
    subdirs = list_log_subdirs()

    if len(subdirs) == 0:
        return "No log subdirectories found."

    return "<br>".join(f"<a href='/view/{subdir}'>{subdir}</a>" for subdir in subdirs)


@route("/view/<subdir>")
@auth_basic(is_authenticated)
def view_subdir_logs(subdir: str):
    subdir_path = os.path.join(LOG_DIR, subdir)

    if not os.path.isdir(subdir_path):
        return f"Subdirectory '{subdir}' does not exist."

    log_files = [
        os.path.join(subdir_path, f)
        for f in os.listdir(subdir_path)
        if os.path.isfile(os.path.join(subdir_path, f))
    ]

    if len(log_files) == 0:
        return f"No log files found in subdirectory '{subdir}'."

    result = subprocess.run(
        [
            "goaccess",
            *log_files,
            "--output",
            "html",
            *GOACCESS_OPTIONS,
        ],
        stdout=subprocess.PIPE,
        check=True,
    )

    return result.stdout.decode("utf-8")


def main():
    run(host="0.0.0.0", port=4876)


if __name__ == "__main__":
    main()
