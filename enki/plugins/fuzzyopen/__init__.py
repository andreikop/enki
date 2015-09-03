from enki.core.core import core
from enki.plugins.fuzzyopen.fuzzyopen import FuzzyOpenCommand


class Plugin:
    def __init__(self):
        core.locator().addCommandClass(FuzzyOpenCommand)

    def del_(self):
        core.locator().removeCommandClass(FuzzyOpenCommand)
