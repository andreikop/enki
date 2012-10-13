"""
ctags --- Generate, update and search tags with using utility ctags
==================================================

This plugin adds to Locator additional command - fuzzy search tags for current document.
Also it adds some menu actions - for generate tags and its update.
"""

from enki.core.core import core
import tags_locator
import tags_generator

class Plugin:
    """Plugin interface
    """
    def __init__(self):
        core.locator().addCommandClass(tags_locator.CommandShowTags)
        self._generator = tags_generator.TagsGenerator()

    def del_(self):
        """Explicitly called destructor
        """
        core.locator().removeCommandClass(tags_locator.CommandShowTags)
