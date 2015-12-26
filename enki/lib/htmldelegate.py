"""
htmldelegate --- QStyledItemDelegate delegate. Draws HTML
=========================================================
"""

from PyQt5.QtWidgets import QApplication, \
                        QStyledItemDelegate, QStyle, QStyleOptionViewItem, \
                        QWidget
from PyQt5.QtGui import QAbstractTextDocumentLayout, \
                        QTextDocument, QPalette
from PyQt5.QtCore import QSize


_HTML_ESCAPE_TABLE = \
    {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        " ": "&nbsp;",
        "\t": "&nbsp;&nbsp;&nbsp;&nbsp;",
    }


def htmlEscape(text):
    """Replace special HTML symbols with escase sequences
    """
    return "".join(_HTML_ESCAPE_TABLE.get(c, c) for c in text)


class HTMLDelegate(QStyledItemDelegate):
    """QStyledItemDelegate implementation. Draws HTML

    http://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt/1956781#1956781
    """
    def __init__(self, parent=None):
        if isinstance(parent, QWidget):
            self._font = parent.font()
        else:
            self._font = None

        QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        """QStyledItemDelegate.paint implementation
        """
        option.state &= ~QStyle.State_HasFocus  # never draw focus rect

        option.state |= QStyle.State_Active  # draw fuzzy-open completion as focused, even if focus is on the line edit

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = QApplication.style() if options.widget is None else options.widget.style()

        doc = QTextDocument()
        if self._font is not None:
            doc.setDefaultFont(self._font)

        doc.setDocumentMargin(1)
        doc.setHtml(options.text)
        #  bad long (multiline) strings processing doc.setTextWidth(options.rect.width())

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(QPalette.Text, option.palette.color(QPalette.Active, QPalette.HighlightedText))

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """QStyledItemDelegate.sizeHint implementation
        """
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        doc = QTextDocument()
        if self._font is not None:
            doc.setDefaultFont(self._font)
        doc.setDocumentMargin(1)
        #  bad long (multiline) strings processing doc.setTextWidth(options.rect.width())
        doc.setHtml(options.text)
        return QSize(doc.idealWidth(), doc.size().height())
