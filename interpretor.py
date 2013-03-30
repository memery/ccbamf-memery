import imp
import os
import os.path
import queue
import sys
import threading
import time

from common import read_json, read_file_or_die
from flatactors import Actor

class InterpretorActor(Actor):
    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.wait_for_message = False
        self.active_threads = []

        general_settings = read_json(read_file_or_die('config/general.json'))
        self.command_prefix = general_settings['command_prefix']

    def main_loop(self, message):
        if message:
            target, source, subject, payload = message
            if subject == 'quit' and source == 'master':
                self.stop()
                return
            elif subject == 'interpret':
                self.spawn_worker_swarm(source, *payload)

        for thread in list(self.active_threads):
            if not thread.is_alive():
                self.active_threads.remove(thread)

    def spawn_worker_swarm(self, source, destination, author, content):
        for plugin_data in list_plugins():
            worker = PluginExecutor(plugin_data, source, destination,
                                    author, content,
                                    self.command_prefix, self.send)
            self.active_threads.append(worker)
            worker.start()



class PluginExecutor(threading.Thread):
    def __init__(self, plugin_data, source, destination, author, content,
                 command_prefix, send_to_master):
        super().__init__()
        self.plugin_data = plugin_data
        self.source = source
        self.destination = destination
        self.author = author
        self.content = content
        self.command_prefix = command_prefix
        self.send_to_master = send_to_master

    def run(self):
        try:
            loaded_plugin = load_plugin(self.plugin_data)
        # TODO: Make these errors much more verbose and informative!
        except ImportError:
            self.send_error('Error when trying to import')
            return
        except SyntaxError:
            self.send_error('Syntax error')
            return
        try:
            response = loaded_plugin.run(self.author, self.content,
                                         self.command_prefix)
        except Exception as e:
            self.send_error('Exception "{}"'.format(e))
            return
        else:
            if response:
                if isinstance(response, list) or isinstance(response, tuple):
                    for item in response:
                        self.send_result(item)
                else:
                    self.send_result(response)


    def send_error(self, error):
        self.respond('logger:errors', 'error', error)

    def send_result(self, result):
        if isinstance(result, str):
            self.respond(self.source, 'response', (self.destination, result))
        else:
            self.send_error('Strange result format "{}" in data: {}'
                            ''.format(type(result), str(result)))

    def respond(self, target, subject, message):
        sender = 'plugin:{}/{}'.format(os.path.basename(self.plugin_data[1]),
                                       self.plugin_data[0])
        self.send_to_master(target, subject, message, sender=sender)


def list_plugins():
    root_path = os.path.join(sys.path[0], 'plugins')
    plugin_dirs = [os.path.join(root_path,d)
                   for d in os.listdir(root_path)
                   if os.path.isdir(os.path.join(root_path,d))]
    plugins = [(os.path.splitext(f)[0], subdir)
               for subdir in plugin_dirs for f in os.listdir(subdir)
               if os.path.splitext(f)[1] == '.py']
    return plugins

def load_plugin(plugin_data):
    plugin_name, plugin_path = plugin_data
    try:
        fp, pathname, description = imp.find_module(plugin_name, [plugin_path])
        plugin = imp.load_module(plugin_name, fp, pathname, description)
    except Exception as e:
        raise e
    else:
        return plugin
    finally:
        try:
            fp.close()
        except UnboundLocalError:
            pass
