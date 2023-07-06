from datetime import datetime


def log(s, newline=False):
    print("\n" + __time() + "  LOG :: " + s) if newline else print(
        __time() + "  LOG :: " + s
    )


def info(s, newline=False):
    print("\n" + __time() + " INFO :: " + s) if newline else print(
        __time() + " INFO :: " + s
    )


def error(s, newline=False):
    print("\n" + __time() + "ERROR :: " + s) if newline else print(
        __time() + "ERROR :: " + s
    )


def __time():
    now = datetime.now()
    current_time = now.strftime("%d/%m/%y::%H:%M:%S")
    return current_time
