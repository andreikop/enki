#!/usr/bin/env python3

import unittest
import os
import os.path
import sys


sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base


RUBY_SOURCE = '''class Person
  def initialize(name, age)
    @name, @age = name, age
  end

def hello_world
    return 7
end
'''


class Test(base.TestCase):

    @base.inMainLoop
    def test_1(self):
        """ Comment the first line """
        qpart = self.createFile('source.rb', RUBY_SOURCE).qutepart
        qpart.cursorPosition = (0, 0)
        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], '# class Person')
        self.assertEqual(qpart.lines[1], '  def initialize(name, age)')

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], 'class Person')
        self.assertEqual(qpart.lines[1], '  def initialize(name, age)')

    @base.inMainLoop
    def test_2(self):
        """ Comment the last line """
        qpart = self.createFile('source.rb', RUBY_SOURCE).qutepart
        qpart.cursorPosition = (7, 0)

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[-2], '    return 7')
        self.assertEqual(qpart.lines[-1], '# end')

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[-2], '    return 7')
        self.assertEqual(qpart.lines[-1], 'end')

    @base.inMainLoop
    def test_3(self):
        """ Comment range """
        qpart = self.createFile('source.rb', RUBY_SOURCE).qutepart
        qpart.selectedPosition = ((1, 0), (2, 27))

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], 'class Person')
        self.assertEqual(qpart.lines[1], '  # def initialize(name, age)')
        self.assertEqual(qpart.lines[2], '  #   @name, @age = name, age')
        self.assertEqual(qpart.lines[3], '  end')

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], 'class Person')
        self.assertEqual(qpart.lines[1], '  def initialize(name, age)')
        self.assertEqual(qpart.lines[2], '    @name, @age = name, age')
        self.assertEqual(qpart.lines[3], '  end')

    @base.inMainLoop
    def test_4(self):
        """ Comment range. Do not include last line """
        qpart = self.createFile('source.rb', RUBY_SOURCE).qutepart
        qpart.selectedPosition = ((1, 0), (3, 0))

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], 'class Person')
        self.assertEqual(qpart.lines[1], '  # def initialize(name, age)')
        self.assertEqual(qpart.lines[2], '  #   @name, @age = name, age')
        self.assertEqual(qpart.lines[3], '  end')

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], 'class Person')
        self.assertEqual(qpart.lines[1], '  def initialize(name, age)')
        self.assertEqual(qpart.lines[2], '    @name, @age = name, age')
        self.assertEqual(qpart.lines[3], '  end')

    @base.inMainLoop
    def test_5(self):
        """ Comment range. Do not include first line """
        qpart = self.createFile('source.rb', RUBY_SOURCE).qutepart
        qpart.selectedPosition = ((3, 0), (1, 0))

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], 'class Person')
        self.assertEqual(qpart.lines[1], '  # def initialize(name, age)')
        self.assertEqual(qpart.lines[2], '  #   @name, @age = name, age')
        self.assertEqual(qpart.lines[3], '  end')

        self.keyClick('Ctrl+U')
        self.assertEqual(qpart.lines[0], 'class Person')
        self.assertEqual(qpart.lines[1], '  def initialize(name, age)')
        self.assertEqual(qpart.lines[2], '    @name, @age = name, age')
        self.assertEqual(qpart.lines[3], '  end')


if __name__ == '__main__':
    unittest.main()
