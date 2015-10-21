from enki.core.core import core
from enki.plugins.fuzzyopen.fuzzyopen import FuzzyOpenCommand, ScanCommand


class Plugin:
    def __init__(self):
        core.locator().addCommandClass(FuzzyOpenCommand)
        core.locator().addCommandClass(ScanCommand)

    def del_(self):
        core.locator().removeCommandClass(FuzzyOpenCommand)
        core.locator().addCommandClass(ScanCommand)
