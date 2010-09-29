#ifndef QTASSISTANTINLINESEARCH_H
#define QTASSISTANTINLINESEARCH_H

#include <QWidget>

class QLineEdit
class QCheckBox
class QLabel
class QToolButton

class QtAssistantInlineSearch : public QWidget
    Q_OBJECT
    friend class QtAssistantChild

public:
    QtAssistantInlineSearch( parent = 0 )

protected:
    void keyPressEvent( QKeyEvent* event )

private slots:
    void updateButtons()

private:
    QLineEdit* editFind
    QCheckBox* checkCase
    QLabel* labelWrapped
    QToolButton* toolNext
    QToolButton* toolClose
    QToolButton* toolPrevious
    QCheckBox* checkWholeWords

signals:
    void findNext()
    void findPrevious()


#endif # QTASSISTANTINLINESEARCH_H
