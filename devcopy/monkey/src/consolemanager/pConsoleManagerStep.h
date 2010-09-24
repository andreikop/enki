#ifndef PCONSOLEMANAGERSTEP_H
#define PCONSOLEMANAGERSTEP_H

#include <objects/MonkeyExport.h>

#include <QString>
#include <QPoint>
#include <QList>
#include <QVariant>

class Q_MONKEY_EXPORT pConsoleManagerStep
public:
    enum Type
        Invalid = -1,
        Error,
        Warning,
        Compiling,
        Finish,
        Unknown,
        Good,
        Bad


    enum CustomRoles
        TypeRole = Qt.UserRole,
        FileNameRole,
        PositionRole


    typedef QMap<int, Data

    pConsoleManagerStep( data = pConsoleManagerStep.Data() )

    bool operator==(  pConsoleManagerStep& other )

    pConsoleManagerStep.Type type()

    QVariant roleValue( int role )
    void setRoleValue( int role, value )

protected:
    Data mData

    static QVariant defaultRoleValue( int role, type )


typedef QList<pConsoleManagerStep> pConsoleManagerStepList

Q_DECLARE_METATYPE( pConsoleManagerStep )
Q_DECLARE_METATYPE( pConsoleManagerStepList )

#endif # PCONSOLEMANAGERSTEP_H
