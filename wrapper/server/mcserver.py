import re
import json
import uuid
import time

from wrapper.server.process import Process
from wrapper.server.player import Player
from wrapper.server.uuid_cache import UUID_Cache
from wrapper.commons import *
from wrapper.exceptions import *

class MCServer:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.config = wrapper.config
        self.log = wrapper.log_manager.get_logger("mcserver")

        self.process = None

        self.state = SERVER_STOPPED
        self.target_state = None

        self.uuid_cache = UUID_Cache()

    def start(self):
        if self.state != SERVER_STOPPED:
            raise StartingException("Server is already running")

        self.log.info("Starting server")

        self.process = Process()
        self.process.start(self.config["server"]["jar"])
        self.state = SERVER_STARTING

        self.players = []
        self.world = None
        self.server_version = None
        self.server_port = None

        self.target_state = (SERVER_STARTED, time.time())

    def stop(self, reason):
        self.target_state = (SERVER_STOPPED, time.time())

    def kill(self):
        self.process.kill()

    # Commands

    def run_command(self, cmd):
        self.process.write("%s\n" % cmd)

    def broadcast(self, msg):
        if type(msg) == dict:
            json_blob = json.dumps(msg)
        else:
            json_blob = json.dumps({
                "text": msg
            })
        self.run_command("tellraw @a %s" % json_blob)

    # Players
    def list_players(self):
        players = []

        for player in self.players:
            # Filters go here

            players.append(player)

        return players

    def get_player(self, username=None, mcuuid=None, ip_address=None):
        for player in self.players:
            if username:
                if username == player.username:
                    return player

            if mcuuid:
                if player.uuid == mcuuid:
                    return player

            if ip_address:
                if player.ip_address == ip_address:
                    return player

    # Tick

    def tick(self):
        # Check if server process is stopped
        if not self.process.process and self.state != SERVER_STOPPED:
            self.log.info("Server stopped")
            self.state = SERVER_STOPPED

        # Check target state, and do accordingly
        target_state, target_state_time = self.target_state
        if target_state == SERVER_STOPPED:

            # Start server shutdown, if it hasn't already started
            if self.state not in (SERVER_STOPPING, SERVER_STOPPED):
                self.run_command("stop")
                self.state = SERVER_STOPPING

            # Check if server shutdown has been going for too long, and kill server
            if self.state == SERVER_STOPPING:
                if time.time() - target_state_time > 60:
                    self.kill()

        # Regex new lines
        for std, line in self.process.console_output:
            # Print line to console
            print(line)

            # Compatible with most recent versions of Minecraft server
            r = re.search("(\[[0-9:]*\]) \[(.*)\/(.*)\](.*)", line)

            # If regex did not match, continue to prevent issues
            if r == None:
                continue

            log_time = r.group(1)
            server_thread = r.group(2)
            log_level = r.group(3)
            output = r.group(4)

            # Parse output
            if self.state == SERVER_STARTING:
                # Grab server version
                if "Starting minecraft" in output:
                    r = re.search(": Starting minecraft server version (.*)", output)
                    server_version = r.group(1)
                    print(server_version)

                # Grab server port
                if "Starting Minecraft server on" in output:
                    r = re.search(": Starting Minecraft server on \*:([0-9]*)", output)
                    server_port = r.group(1)
                    print(server_port)

                # Grab world name
                if "Preparing level" in output:
                    r = re.search(": Preparing level \"(.*)\"", output)
                    self.world = r.group(1)

                # Server started
                if "Done" in output:
                    self.state = SERVER_STARTED
                    self.run_command("gamerule sendCommandFeedback false")
            if self.state == SERVER_STARTED:
                # UUID catcher
                if "User Authenticator" in server_thread:
                    r = re.search(": UUID of player (.*) is (.*)", output)

                    if r:
                        username, uuid_string = r.group(1), r.group(2)
                        uuid_obj = uuid.UUID(hex=uuid_string)

                        self.uuid_cache.add(username, uuid_obj)

                # Player Join
                r = re.search(": (.*)\[/(.*):(.*)\] logged in with entity id (.*) at \((.*), (.*), (.*)\)", output)
                if r:
                    username = r.group(1)
                    ip_address = r.group(2)
                    entity_id = r.group(4)
                    position = [
                        float(r.group(5)),
                        float(r.group(6)),
                        float(r.group(7))
                    ]

                    uuid_obj = self.uuid_cache.get(username)

                    player = Player(username=username, uuid=uuid_obj)

                    self.players.append(player)

                    print(username, ip_address, entity_id, position)

                # Player Disconnect
                r = re.search(": (.*) lost connection: (.*)", output)
                if r:
                    username = r.group(1)
                    server_disconnect_reason = r.group(2)

                    player = self.get_player(username=username)
                    if player:
                        print("Removing %s from players" % player)
                        self.players.remove(player)

                # Chat messages
                r = re.search(": <(.*)> (.*)", output)
                if r:
                    username, message = r.group(1), r.group(2)
                    print(username, message)

        # Dirty hack, let's make this better later using process.read_console()
        self.process.console_output = []