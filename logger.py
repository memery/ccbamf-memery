import common

class LoggerActor(common.Actor):
    def main_loop(self, message):
        if message:
            print(message)
