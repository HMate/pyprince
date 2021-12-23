# TODO: Make log configurable globally. Logging to stdout only works for tests.
# It breaks autmated usage, because we use stdout to give back a json result.
def log(msg):
    print(msg)
