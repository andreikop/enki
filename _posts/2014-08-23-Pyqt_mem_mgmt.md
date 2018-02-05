---
layout: post
title: PyQt. How to shoot yourself in the foot
baseurl: ../../../
---

## PyQt. How to shoot yourself in the foot.

Once upon a time there was a programming language called C. And it had 2 memory management functions: `malloc()` and `free()`. But it was too complicated.
Bjarne Stroustrup decided that C memory management should be easier. So he invented C++. In addition to`malloc()` and `free()`, C++ had `new`, `delete`, destructors, RAII, auto and shared pointers.
Guido van Rossum found that C++ was also not simple enough. He chose another way and invented Python - a language which doesn't have even `malloc()` or `free()`.
Meanwhile Norwegian trolls created the C++ GUI library Qt. It simplifies memory management by deleting objects automatically when it thinks the objects are not needed.
A man called Phil Thompson was upset that a cool library like Qt doesn't exist in the excellent Python language. He combined them in the PyQt project. But it is not so easy to combine different memory management paradigms. Let's see what the pitfalls are.
*(Text above is a fairy tale. Text below contains code and technical information)*

PyQt works in the following way: every public C++ class has a wrapper class in Python. A Python programmer works with a wrapper and the wrapper calls a real C++ object internally.
All is well if an object and a wrapper are created and deleted simultaneously. But it is possible to break the lifetime synchronization. I personally know 3 ways:

* Python wrapper is created but C++ object isn't
* Python wrapper is garbage-collected but C++ object still exists
* C++ object is deleted by Qt but Python wrapper still exists

#### Python wrapper is created but C++ object isn't
```python
    from PyQt4.QtCore import QObject

    class MyObject(QObject):
        def __init__(self):
        self.field = 7

    obj = MyObject()
    print(obj.field)
    obj.setObjectName("New object")

>>> Traceback (most recent call last):
>>> File "pyinit.py", line 9, in <module>
>>> obj.setObjectName("New object")
>>> RuntimeError: '__init__' method of object's base class (MyObject) not called.
```

This and other code is available [here](https://github.com/andreikop/pyqt-memory-mgmt)

`MyObject` constructor doesn't call the constructor of the base class. MyObject is successfully created and can be used. But when the C++ method is called, a `RuntimeError` is issued. The exception explains what is wrong.

Fixed code:

```python
    class MyObject(QObject):
        def __init__(self):
        QObject.__init__(self)
```

#### Python wrapper is deleted by the garbage collector

```python
    from PyQt4.QtGui import QApplication, QLabel

    def createLabel():
        label = QLabel("Hello, world!")
        label.show()

    app = QApplication([])
    createLabel()

    app.exec_()
```

If this code is written in C++, after `app.exec_()` we see a window with "Hello, world!". But this code doesn't show any windows. When the `createLabel()` function finishes its execution, the Python code doesn't have any references to the label. The careful garbage collector deletes the Python wrapper. And the wrapper deletes the C++ object.
Fixed code:

```python
    from PyQt4.QtGui import QApplication, QLabel

    def createLabel():
        label = QLabel("Hello, world!")
        label.show()
        return label

    app = QApplication([])
    label = createLabel()

    app.exec_()
```

References to all created objects must be saved even if you are not going to use them.

### C++ object is deleted by Qt but Python wrapper still exists

The first two cases are described in the PyQt and PySide documentation and are quite simple. Things are much more complicated if a Python wrapper doesn't know that Qt has deleted an object.
Qt may delete an object when a parent object has been deleted, when the window is closed, when `deleteLater()` is called, and in some other cases.
If a C++ object has been deleted, it is still possible to work with pure-Python methods of a wrapper but C++ wrapper access leads to exceptions and crashes.

Let's start from a very simple way to shoot ourselves in the foot:

```python
    from PyQt4.QtCore import QTimer
    from PyQt4.QtGui import QApplication, QWidget

    app = QApplication([])

    widget = QWidget()
    widget.setWindowTitle("Dead widget")
    widget.deleteLater()

    QTimer.singleShot(0, app.quit) # Make the application quit just after start
    app.exec_() # Execute the application to call deleteLater()

    print(widget.windowTitle())
>>> Traceback (most recent call last):
>>> File "1_basic.py", line 20, in <module>
>>> print(widget.windowTitle())
>>> RuntimeError: wrapped C/C++ object of type QWidget has been deleted
```

We create QWidget and ask Qt to delete it. During `app.exec_()` the object is deleted. But the wrapper doesn't know about it. When the wrapper calls `windowTitle()`, `RuntimeError` is generated or the application crashes.
Of course if a programmer has called `deleteLater()` and then uses an object, it is his own fault. But real life code often contains more complex scenarios:

* Object is created
* External signals are connected to object slots
* Qt deletes the object. i.e. when a window is closed
* A slot of the deleted object is called by timer or signal from the external world
* The application crashes or generates an exception

[Long real life code example](https://github.com/andreikop/pyqt-memory-mgmt/blob/master/4-reallife.py)

#### When slots are disconnected automatically

In a C++ application, when object is deleted, all slots are disconnected automatically. But in some cases PyQt and PySide can't disconnect an object. I was curious to know what these cases are. During my experiments [this test](https://github.com/andreikop/pyqt-memory-mgmt/blob/master/5-disconnect.py) was created.

I discovered that the result depends on the method's programming language. And the behaviour differs for PyQt and PySide.

| Slot type | PyQt | PySide |
| --------------------------------------- | ------------------ | ----------------|
| С++ method | is disconnected | is disconnected |
| Pure-Python method | crashes | is disconnected |
| C++ method overridden by Python wrapper | crashes | crashes |

**Update:** My test uses new style signals and slots. It was found during discussion that old style signals are always disconnected automatically.

#### The solution

It is especially difficult to solve problems connected to C++ object deletion. Such problems may be hidden for a long time. If an application crashes, it might not be clear why. But here are some tips. If you use new style signals:

* When deleting an object which has Python-slots, disconnect the slots manually
* To be notified about an object deletion use the `QObject.destroyed` signal but not the `__del__` method of a Python wrapper
* Don't use `QTimer.singleShot` for an object which might be deleted. It is impossible to stop and disconnect such a timer
* Don't use lambda function as a slot. It is impossible to disconnect it.

~~Does the silver bullet exist? Are there other ways to decrease probability of crashes? I'll be happy to read your comments.~~
**Update:** Yuya Nishihara discovered that old style slots are always disconnected. It seems like it is the silver bullet.


### The conclusion

I hope you are not scared of PyQt and PySide now? You shouldn't be. In real projects you don't often face problems when using the libraries. Every tool has strengths and weaknesses. You just need to know them and you will live happily ever after.
