"""
htmldelegate --- QStyledItemDelegate delegate. Draws HTML
=========================================================
"""

from PyQt4 import QtGui
from PyQt4 import QtCore

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
    return "".join(_HTML_ESCAPE_TABLE.get(c,c) for c in text)


class HTMLDelegate(QtGui.QStyledItemDelegate):
    """QStyledItemDelegate implementation. Draws HTML
    
    http://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt/1956781#1956781
    """
    
    def paint(self, painter, option, index):
        """QStyledItemDelegate.paint implementation
        """
        option.state &= ~QtGui.QStyle.State_HasFocus  # never draw focus rect
        
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)

        style = QtGui.QApplication.style() if options.widget is None else options.widget.style()

        doc = QtGui.QTextDocument()
        doc.setDocumentMargin(1)
        doc.setHtml(options.text)
        #  bad long (multiline) strings processing doc.setTextWidth(options.rect.width())

        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter);

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        #if (optionV4.state & QStyle::State_Selected)
            #ctx.palette.setColor(QPalette::Text, optionV4.palette.color(QPalette::Active, QPalette::HighlightedText));

        textRect = style.subElementRect(QtGui.QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """QStyledItemDelegate.sizeHint implementation
        """
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)

        doc = QtGui.QTextDocument()
        doc.setDocumentMargin(1)
        #  bad long (multiline) strings processing doc.setTextWidth(options.rect.width())
        doc.setHtml(options.text)
        return QtCore.QSize(doc.idealWidth(), doc.size().height())
