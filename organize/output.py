from typing import Protocol

from .resource import Resource


class Output(Protocol):
    def start(self, simulate: bool):
        pass

    def info(self, res: Resource, msg):
        pass

    def warning(self, res: Resource, msg):
        pass

    def error(self, res: Resource, msg):
        pass

    def prompt(self, res: Resource, msg) -> str:
        pass

    def confirm(self, res: Resource, msg) -> bool:
        pass


class RichOutput:
    def start(self, simulate: bool):
        print("start", simulate)

    def info(self, res: Resource, msg):
        print("info", res, msg)

    def warning(self, res: Resource, msg):
        print("warning", res, msg)

    def error(self, res: Resource, msg):
        print("error", res, msg)

    def prompt(self, res: Resource, msg) -> str:
        print("prompt", res, msg)
        return "nothing"

    def confirm(self, res: Resource, msg) -> bool:
        print("confirm", res, msg)
        return True
