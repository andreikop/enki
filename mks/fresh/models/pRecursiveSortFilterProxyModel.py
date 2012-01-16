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
