import time

class Timer(object):
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        end = time.time()
        msecs = (end - self.start) * 1000
        print('{}: {} ms'.format(self.message, int(msecs)))