import fcntl
import json
import logging
import os
import pty
import re
import select
import shutil
import signal
import struct
import subprocess
import termios
import threading

from channels.generic.websocket import WebsocketConsumer
from django.apps import apps
from django.conf import settings
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType

from .models import TerminalCommand

DEFAULT_COMMANDS = [
    ["./manage.py", "shell_plus"],
    ["./manage.py", "shell"],
    ["/bin/bash"],
]


class TerminalConsumer(WebsocketConsumer):
    child_pid = None
    fd = None
    shell = None
    command = []
    user = None
    subprocess = None
    authorized = False
    connected = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        configured_commands = getattr(
            settings, "DJANGO_ADMIN_SHELLX_COMMANDS", DEFAULT_COMMANDS
        )
        # Check if each command is available in the system
        for command in configured_commands:
            path = shutil.which(command[0])
            if path:
                if "shell_plus" in command:
                    if apps.is_installed("django_extensions"):
                        self.command = command
                        break
                    continue

                self.command = command
                break

    def run_command(self):

        master_fd, slave_fd = pty.openpty()

        self.fd = master_fd

        with subprocess.Popen(  # pylint: disable=subprocess-popen-preexec-fn
            self.command,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=os.setsid,
        ) as proc:
            self.subprocess = proc
            self.child_pid = proc.pid
            proc.wait()

            # Subprocess has finished, close the websocket
            # happens when process exits, either via user exiting using exit() or by error
            self.subprocess = None
            self.child_pid = None
            if self.connected:
                self.connected = False
                self.close(4030)

    def connect(self):

        if not "user" in self.scope:
            self.close(4401)
            return

        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            self.close(4401)
            return

        if getattr(settings, "DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY", True):
            if not self.user.is_superuser:
                self.close(4403)
                return

        if self.child_pid is not None:
            return

        if self.user.is_authenticated:
            self.connected = True
            self.authorized = True
            self.accept()

        # Daemonize the thread so it automatically dies when the main thread exits
        thread = threading.Thread(target=self.run_command, daemon=True)
        thread.start()

        thread = threading.Thread(target=self.read_from_pty, daemon=True)
        thread.start()

    def read_from_pty(self):
        while True:
            select.select([self.fd], [], [])
            output = os.read(self.fd, 1024)
            if not output:
                break
            message = output.decode(errors="ignore")
            self.send(text_data=json.dumps({"message": message}))

    def resize(self, row, col, xpix=0, ypix=0):
        winsize = struct.pack("HHHH", row, col, xpix, ypix)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def write_to_pty(self, message):
        os.write(self.fd, message.encode())

    def kill_pty(self):
        if self.subprocess is not None:
            os.killpg(os.getpgid(self.child_pid), signal.SIGTERM)
            self.subprocess = None
            self.child_pid = None

    def disconnect(self, code):
        self.connected = False
        self.kill_pty()

    def map_terminal_prompt(self, terminal_prompt):

        if "reverse-i-search" in terminal_prompt or "I-search" in terminal_prompt:
            return None, None, True

        mapped = False
        command = None
        prompt = None

        # pattern >>> TerminalCommand.objects.all()
        match_1 = re.match(r">>> ?(.*)", terminal_prompt)
        # pattern In [2]: TerminalCommand.objects.all()'
        match_2 = re.match(r"In \[.*\]: ?(.*)", terminal_prompt)
        # [adin@adin test]$ echo 'hello world'
        match_3 = re.match(r".*[#|$] ?(.+)", terminal_prompt)

        if match_1:
            command = match_1.group(1)
            prompt = "django-shell"
            mapped = True
        elif match_2:
            command = match_2.group(1)
            prompt = "django-shell"
            mapped = True
        elif match_3:
            command = match_3.group(1)
            prompt = "shell"
            mapped = True
        else:
            logging.debug("Could not extract command from prompt: %s", terminal_prompt)

        return command, prompt, mapped

    def save_command_history(self, command):
        command, prompt, mapped = self.map_terminal_prompt(command)

        # Ignore successful mappings but empty command
        # e.g user pressing enter or using search history
        if not command and mapped:
            logging.debug("Ignoring empty command")
            return

        if not command:
            logging.warning("No command to save")
            return

        tc, _ = TerminalCommand.objects.get_or_create(
            command=command, prompt=prompt, defaults={"created_by": self.user}
        )
        tc.execution_count += 1
        tc.save()

        # Create a log entry for the command
        LogEntry.objects.log_action(
            user_id=self.user.id,
            content_type_id=ContentType.objects.get_for_model(tc).pk,
            object_id=tc.id,
            object_repr=str(tc),
            action_flag=CHANGE,
            change_message={"changed": {"name": "action", "object": tc.command}},
        )

    def receive(self, text_data=None, bytes_data=None):
        if not self.authorized:
            return

        if not text_data:
            logging.debug("No data received")
            return

        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            logging.warning("Could not decode JSON: %s", text_data)
            return

        action = text_data_json.get("action")

        if action == "resize":
            self.resize(text_data_json["data"]["rows"], text_data_json["data"]["cols"])
        elif action in ["input", "save_history"]:
            if action == "input":
                message = text_data_json["data"]["message"]
                self.write_to_pty(message)
            else:
                if text_data_json["data"]["command"]:
                    self.save_command_history(text_data_json["data"]["command"])
        elif action == "kill":
            self.kill_pty()
            self.send(text_data=json.dumps({"message": "Terminal killed"}))
        else:
            logging.info("Unknown action: %s,", text_data_json["action"])
