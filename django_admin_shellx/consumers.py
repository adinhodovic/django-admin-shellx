# chat/consumers.py
import fcntl
import json
import logging
import os
import pty
import select
import struct
import subprocess
import termios
import threading

from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType

from .models import TerminalCommand


class TerminalConsumer(WebsocketConsumer):
    child_pid = None
    fd = None
    shell = None
    user = None
    subprocess = None
    authorized = False

    def save_command_history(self, command, prompt=None):
        if not command:
            logging.warning("No command to save")
            return

        # TODO: Add prompt? prompt=prompt
        tc, _ = TerminalCommand.objects.get_or_create(
            command=command, created_by=self.user
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

    def connect(self):
        self.accept()

        self.user = self.scope["user"]

        if not self.user or not self.user.is_authenticated:
            self.close(4401)
            return

        self.authorized = True

        if getattr(settings, "DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY", False):
            if not self.user.is_superuser:
                self.close(4403)
                return

        if self.child_pid is not None:
            return

        master_fd, slave_fd = pty.openpty()

        self.fd = master_fd

        self.subprocess = subprocess.Popen(
            ["bash"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=os.setsid,
        )
        self.child_pid = self.subprocess.pid

        thread = threading.Thread(target=self.read_from_pty)
        thread.daemon = True  # Daemonize the thread so it automatically dies when the main thread exits
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
        logging.info(f"Resizing terminal to {row}x{col}")
        winsize = struct.pack("HHHH", row, col, xpix, ypix)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def write_to_pty(self, message):
        os.write(self.fd, message.encode())

    def kill_pty(self):
        if self.subprocess is not None:
            self.subprocess.kill()
            self.subprocess = None
            self.child_pid = None

    def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        self.subprocess.terminate()

    def receive(self, text_data=None, bytes_data=None):
        if not self.authorized:
            return

        if not text_data:
            logging.debug("No data received")
            return

        text_data_json = json.loads(text_data)

        action = text_data_json.get("action")

        if action == "resize":
            self.resize(text_data_json["data"]["rows"], text_data_json["data"]["cols"])
        elif action in ["input", "save_history"]:
            if action == "input":
                message = text_data_json["data"]["message"]
                self.write_to_pty(message)
            else:
                self.save_command_history(
                    text_data_json["data"]["command"], text_data_json["data"]["prompt"]
                )
        elif action == "kill":
            self.kill_pty()
            self.send(text_data=json.dumps({"message": "Terminal killed"}))
        else:
            logging.info(f"Unknown action: {text_data_json['action']}")
