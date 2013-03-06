
from common import spawn_actor, Actor
import logger
import input_

class MasterActor(Actor):
    def __init__(self, parent_inbox):
        # TEMPORARY
        super().__init__(parent_inbox)
        self.daemon = False

    def initialize(self):
        self.nodes = {
            'logger': spawn_actor(logger.LoggerActor),
            'input': spawn_actor(input_.InputActor, self.inbox)
        }

    def main_loop(self, message):
        if message:
            self.nodes['logger'].write_to(message)

if __name__ == "__main__":
    main_actor = spawn_actor(MasterActor)
