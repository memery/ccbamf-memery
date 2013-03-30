import imp
import os
import os.path
import queue
import sys
import threading
import time

from common import Actor

class InterpretorActor(Actor):
    def constructor(self):
        self.daemon = False

    def initialize(self):
        self.wait_for_message = False
        self.active_threads = []

    def main_loop(self, message):
        if message:
            target, source, subject, payload = message
            if subject == 'quit' and source == 'master':
                self.stop()
                return
            elif subject == 'interpret':
                self.spawn_worker_swarm(source, *payload)

        for item in list(self.active_threads):
            q, thread, birthdate = item
            try:
                data = q.get_nowait()
            except queue.Empty:
                pass
            else:
                subject, content = data
                if subject == 'response':
                    target, destination, response = content
                    self.send(target, 'response', (destination, response))
                elif subject == 'error':
                    self.send('logger:error', None, content)
            if not thread.is_alive():
                self.active_threads.remove(item)

    def spawn_worker_swarm(self, source, destination, author, content):
        for plugin_data in list_plugins():
            q = queue.Queue()
            timestamp = time.time()
            worker = PluginExecutor(plugin_data, source, destination, author, content, q)
            self.active_threads.append((q, worker, timestamp))
            worker.start()



class PluginExecutor(threading.Thread):
    def __init__(self, plugin_data, source, destination, author, content, response_queue):
        super().__init__()
        self.plugin_data = plugin_data
        self.source = source
        self.destination = destination
        self.author = author
        self.content = content
        self.response_queue = response_queue

    def run(self):
        try:
            loaded_plugin = load_plugin(self.plugin_data)
        except ImportError:
            self.respond('error', 'Could not import {}'.format(self.plugin_data))
            return
        response = loaded_plugin.run(self.author, self.content)
        if response:
            self.respond('response', (self.source, self.destination, response))

    def respond(self, subject, message):
        self.response_queue.put((subject, message))


def list_plugins():
    root_path = os.path.join(sys.path[0], 'plugins')
    plugin_dirs = [os.path.join(root_path,d)
                   for d in os.listdir(root_path)
                   if os.path.isdir(os.path.join(root_path,d))]
    plugins = [(os.path.splitext(f)[0], os.path.join('plugins', subdir))
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
