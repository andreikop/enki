A long time ago C language existed. And it has 2 memory management functions: `malloc` and `free`. But it was too complicated.
Bjarne Stroustrup found that C memory management should be easier. And invented C++. Except `malloc` and `free` C++ includes `new`, `delete`, destructors, RAII, auto and shared pointers.
Guido van Rossum found that C++ is also not enough simple. He chose another way and invented Python, which doesn't include even `malloc` and `free`.
Meanwhile Norwegian trolls invented C++ GUI library Qt. It simplifies memory management by deleting objects automatically when it think the objects are not needed.
Phil Thompson was upset, that cool library Qt doesn't exist in exelent language Python. And combined them in PyQt project. But, it is not so easy to combine different memory management paradigms. There are some side effects. Let's check which one...
*(Text above is a fairy tale. Text below contains code and technical information)*

PyQt works the next way: every public C++ class has a wrapper class in Python. Python programmer works with the wrapper, and the wrapper calls true C++ object when needed.
All is well if an object and a wrapper is created and deleted simultaneously. But it is possible to break the lifetime syncronisation. I know 3 ways:
* Python wrapper was created but C++ object wasn't
* Python wrapper was deleted by the garbadge collector
* C++ object was deleted by Qt, but Python wrapper still exists

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

`MyObject` constructor doesn't call the constructor of the base class. MyObject was sucessully created, it can be used. But when C++ method is accessed, `RuntimeError` is issued. The exceptinon explain, what is wrong.

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

If this code were written in C++ after `app.exec_()` we would see window with "Hello, world". But this code will not show any windows When createLabel() function has finished its execution, Python code didn't have and references to the label, and careful garbadge collector has deleted Python-wrapper. And the wrapper has deleted C++ object.
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

References to all created objects shall be saved even if you are not going to use this references.

### Qt удалила объект. Python-обертка жива

Two the first cases are described in the PyQt/Pyside documentation and are quite simple. Things are much more complicated, if Python wrapper doesn't know, that Qt has deleted an object.
Qt may delete an object when a parent object was deleted, when window is closed, when `deleteLater()` is called and in some other cases.
If a C++ object has been deleted, it is still possible to work with pure-Python methods of a wrapper, but C++ wrapper access leads to RuntimeError and crashes.

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

We created QWidget and asked Qt to delete it. During `app.exec_()` the object will be deleted. But a wrapper doesn't know about it. When wrapper calls `windowTitle() RuntimeError will be generated or the application will crash.
Of course if a programmer has called `deleteLater()` and than uses an object, it is he who is gilty. But real life code often contains more complex scenario:

* Object is created
* External signals are connected to object slots
* Qt deletes object. i.e. when a window is closed
* A slot of the deleted object is called by timer or signal from the external world.
* The application crashes or generates an exceptinon

[Long real life code example](https://github.com/hlamer/pyqt-memory-mgmt/blob/master/4-reallife.py)

#### When slots are disconnected automatically

In a C++ application when object is deleted all slots are disconnected automatically. But PyQt and PySide not always can disconnect an object. I was curious in which cases slots are not disconnected. During experiments next [test](https://github.com/hlamer/pyqt-memory-mgmt/blob/master/5-disconnect.py) was created.

I discovered that result depends on which slots of a deleted object were connected to signals. And the behaviour differs on PyQt and Pyside.

| Slot type                               | PyQt               | PySide          |
| --------------------------------------- | ------------------ | ----------------|
| С++ method                              | is disconnected    | is disconnected |
| Pure-Python method                      | crashes            | is disconnected |
| C++ method overriden by Python wrapper  | crashes            | crashes |

The solution

It is especially difficult to solve problems connected to C++ objects deletion. Such problems sometimes are no visible for a long time. If an application crashes, it is not clear, why. But here is a few advices:
* If deleting an object which has Python-slots, disconnect the slots manually.
* Use QObject.destroyed signal to get notified about an object deletion, but not `__del__` method of a Python wrapper.
* Don't use QTimer.singleShot for an object which may be deleted. It is impossible to stop and disconnect such a timer.

I'll be happy to read about a silver bullet in the commentaries if it exists.


### The conclusion

I hope you a not scared of PyQt and PySide now? You should not. In real live you don't often face any problems when using the libraries. Every tool has strengths and weaknesses. You just should know them.

If you are having any question and comments, you are welcome to [Enki editor](http://enki-editor.org) blog.
