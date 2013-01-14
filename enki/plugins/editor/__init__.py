"""
editor --- Text editor component. Uses Qutepart internally
==========================================================
"""

from enki.core.core import core

from enki.plugins.editor.editor import Editor

class Plugin:
    """Plugin interface implementation
    
    Installs and removes editor from the system
    """
    def __init__(self):
        core.workspace().setTextEditorClass(Editor)
    
    def del_(self):
        core.workspace().setTextEditorClass(None)

