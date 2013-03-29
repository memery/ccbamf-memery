import common

class LoggerActor(common.Actor):
    def main_loop(self, message):
        _, _, _, payload = message
        print(payload)
