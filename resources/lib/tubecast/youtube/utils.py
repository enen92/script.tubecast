# -*- coding: utf-8 -*-
import ast
import re
from collections import namedtuple

from resources.lib.kodi import kodilogging

logger = kodilogging.get_logger()

Command = namedtuple("Command", ("code", "name", "data"))


def _command_from_match(match):
    code = int(match.group("code"))
    name = match.group("cmd")
    raw_data = match.group("data")
    if raw_data:
        data = ast.literal_eval(raw_data)
    else:
        data = None

    return Command(code, name, data)


CMD_PATTERN = re.compile(r"\[(?P<code>\d+),\[\"(?P<cmd>.+?)\"(?:,(?P<data>.*?))?\]\]")


class CommandParser:
    def __init__(self, buf=None):
        self.pending = ""

        if buf:
            self.write(buf)

    def __iter__(self):
        return self._parse_pending()

    def _parse_pending(self):
        if not self.pending:
            return

        for match in CMD_PATTERN.finditer(self.pending):
            self.pending = self.pending[match.end():]

            try:
                cmd = _command_from_match(match)
            except SyntaxError:
                logger.exception("unable to parse command")
            else:
                yield cmd

    def write(self, s):  # type: (str) -> None
        for line in s.splitlines():
            self.pending += line

    def get_commands(self):  # type: () -> List[Command]
        return list(self)


def get_video_list(data):
    videos = []
    if "videos" in list(data.keys()):
        videos = data["videos"]
    return videos
