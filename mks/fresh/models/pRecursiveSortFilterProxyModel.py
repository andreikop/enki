"""This file has been ported from fresh library by Azevedo Filippe aka PasNox

See information at https://github.com/pasnox/fresh and 
API docks at http://api.monkeystudio.org/fresh/
"""

from PyQt4.QtGui import QSortFilterProxyModel

class pRecursiveSortFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index( source_row, 0, source_parent )
        rowCount = self.sourceModel().rowCount( index )
        accepted = QSortFilterProxyModel.filterAcceptsRow( self, source_row, source_parent )
        
        if rowCount > 0 and not accepted :
            for row in range(rowCount):
                if  self.filterAcceptsRow(row, index):
                    return True
    
        return accepted
