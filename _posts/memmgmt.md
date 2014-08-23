A long time ago C language existed. And it has 2 memory management functions: `malloc` and `free`. But it was too complicated.
Bjarne Stroustrup found that C memory management should be easier. And invented C++. Except `malloc` and `free` C++ had `new`, `delete`, destructors, RAII, auto and shared pointers.
Guido van Rossum found that C++ is also not enough simple. He chose another way and invented Python - a language which doesn't have even `malloc` and `free`.
Meanwhile Norwegian trolls created C++ GUI library Qt. It simplifies memory management by deleting objects automatically when it thinks the objects are not needed.
Phil Thompson was upset that cool library Qt doesn't exist in exelent language Python. He combined them in PyQt project. But it is not so easy to combine different memory management paradigms. Let's see what are the check what are the pifalls of such combination...
*(Text above is a fairy tale. Text below contains code and technical information)*

PyQt works the next way: every public C++ class has a wrapper class in Python. Python programmer works with a wrapper and a wrapper calls a real C++ object.
All is well if an object and a wrapper is created and deleted simultaneously. But it is possible to break the lifetime syncronisation. I know 3 ways:
* Python wrapper was created but C++ object wasn't
* Python wrapper was garbadge-collected but C++ object still exists
* C++ object was deleted by Qt but Python wrapper still exists

### Python wrapper was created but C++ object wasn't

```
from PyQt4.QtCore import QObject

    class MyObject(QObject):
        def __init__(self):
            self.field = 7

    obj = MyObject()
    print(obj.field)
    obj.setObjectName("New object")

>>> Traceback (most recent call last):
>>>   File "pyinit.py", line 9, in <module>
>>>     obj.setObjectName("New object")
>>> RuntimeError: '__init__' method of object's base class (MyObject) not called.
```

This and other code is available [here](https://github.com/hlamer/pyqt-memory-mgmt)

`MyObject` constructor doesn't call the constructor of the base class. MyObject is sucessully created, it can be used. But when C++ method is called, `RuntimeError` is issued. The exceptinon explains what is wrong.

Fixed code:
```
    ...
    class MyObject(QObject):
        def __init__(self):
            QObject.__init__(self)
    ...
```

### Python wrapper was deleted by the garbadge collector

```
   from PyQt4.QtGui import QApplication, QLabel

    def createLabel():
        label = QLabel("Hello, world!")
        label.show()

    app = QApplication([])
    createLabel()

    app.exec_()
```

If this code were written in C++, after `app.exec_()` we would see a window with "Hello, world". But this code will not show any windows. When `createLabel()` function has finished its execution Python code doesn't have any references to the label. Careful garbadge collector deletes the Python wrapper. And the wrapper deletes C++ object.
Fixed code:

```
    from PyQt4.QtGui import QApplication, QLabel

    def createLabel():
        label = QLabel("Hello, world!")
        label.show()
        return label

    app = QApplication([])
    label = createLabel()

    app.exec_()
```

References to all created objects shall be saved even if you are not going to use them.

### C++ object was deleted by Qt but Python wrapper still exists

Two the first cases are described in the PyQt/Pyside documentation and are quite simple. Things are much more complicated if a Python wrapper doesn't know that Qt has deleted an object.
Qt may delete an object when a parent object was deleted, when window is closed, when `deleteLater()` is called and in some other cases.
If a C++ object has been deleted, it is still possible to work with pure-Python methods of a wrapper but C++ wrapper access leads to `RuntimeError` and crashes.

Let's start from very simple way to shoot ones leg:

```
    from PyQt4.QtCore import QTimer
    from PyQt4.QtGui import QApplication, QWidget


    app = QApplication([])

    widget = QWidget()
    widget.setWindowTitle("Dead widget")
    widget.deleteLater()

    QTimer.singleShot(0, app.quit)  # Make the application quit just after start
    app.exec_()  #  Execute the application to call deleteLater()

    print(widget.windowTitle())
>>> Traceback (most recent call last):
>>>   File "1_basic.py", line 20, in <module>
>>>     print(widget.windowTitle())
>>> RuntimeError: wrapped C/C++ object of type QWidget has been deleted
```

We create QWidget and ask Qt to delete it. During `app.exec_()` the object will be deleted. But a wrapper doesn't know about it. When wrapper calls `windowTitle()` `RuntimeError` is generated or the application crashes.
Of course if a programmer has called `deleteLater()` and than uses an object, it is he who is gilty. But real life code often contains more complex scenario:

* Object is created
* External signals are connected to object slots
* Qt deletes the object. i.e. when a window is closed
* A slot of the deleted object is called by timer or signal from the external world
* The application crashes or generates an exceptinon

[Long real life code example](https://github.com/hlamer/pyqt-memory-mgmt/blob/master/4-reallife.py)

#### When slots are disconnected automatically

In a C++ application when object is deleted all slots are disconnected automatically. But in some cases PyQt and PySide can't disconnect an object. I was curious what are the cases. During my experiments next [test](https://github.com/hlamer/pyqt-memory-mgmt/blob/master/5-disconnect.py) was created.

I discovered that result depends on a method programming language. And the behaviour differs for PyQt and Pyside.

| Slot type                               | PyQt               | PySide          |
| --------------------------------------- | ------------------ | ----------------|
| С++ method                              | is disconnected    | is disconnected |
| Pure-Python method                      | crashes            | is disconnected |
| C++ method overriden by Python wrapper  | crashes            | crashes         |

#### The solution

It is especially difficult to solve problems connected to C++ objects deletion. Such problems may be hidden for a long ime. If an application crashes, it is not clear, why. But here are some advices:
* When deleting an object which has Python-slots, disconnect the slots manually
* To get notified about an object deletion use `QObject.destroyed` signal but not `__del__` method of a Python wrapper
* Don't use `QTimer.singleShot` for an object which may be deleted. It is impossible to stop and disconnect such a timer

Does the silver bullet exist? Are there other ways to decrease probability of crashes? I'll be happy to read about it in the commentaries.


### The conclusion

I hope you a not scared of PyQt and PySide now? You should not. In real projects you don't often face any problems when using the libraries. Every tool has strengths and weaknesses. You just should know them.

If you are having any questions and comments, you are welcome to [Enki editor](http://enki-editor.org) blog.
