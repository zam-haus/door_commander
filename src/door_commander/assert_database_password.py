from .settings import POSTGRES_DB
if POSTGRES_DB:
    from .settings import POSTGRES_PASSWORD, DEBUG

    if DEBUG:
        print("DB password assertion skipped due to debug mode.")
    else:
        if POSTGRES_PASSWORD in (None, "", "password", "POSTGRES_PASSWORD"):
            raise Exception(
                "Please specify a non-default password for your database -- refusing to connect with password {!r}.".format(
                    POSTGRES_PASSWORD))
        else:
            print("DB password assertion successful.")