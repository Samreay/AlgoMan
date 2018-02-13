from pydispatch import dispatcher
import numpy as np


def digest_raw(data):
    print(data)


if __name__ == "__main__":
    # Load digested
    pass
    # Check raw
    pass
    # Subscribe to new raw
    pass

    dispatcher.connect(digest_raw, signal="raw_data", sender=dispatcher.Any)
    input("Press enter to terminate")

    # pub anything new