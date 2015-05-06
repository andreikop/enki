# Welcome to the VIM Tutor for Enki

Welcome to Vim mode tutorial of Enki editor. Vim is a very powerful editor, which implements a wonderful idea of editing text with alphanumeric keyboard. Enki has a special mode, which allows you to use this mode.

The mode will look weird and complicated at the beginning, but spend 20 minutes on completing this tutorial, than a few days on getting habitual to the mode, and it is varrantied, that you will edit text quicker and get tired less!

You'll realize that you've been crawling and now can fly!

This tutorial is based on version 1.7 of original Vim Tutorial. It is going to describe enough commands to start using Vim mode effectivelly.

It is important to remember that this tutor is set up to teach by use.  That means that you need to execute the commands to learn them properly.  If you only read the text, you will forget the commands!

It could be easier to read this tutorial if you open the Preview dock. **But do the edit operation on the code!**

NOTE: when you've finished with the tutorial, read [commands reference](https://github.com/hlamer/enki/wiki/Vim)

-----------------------------------------------------------------------------
## Lesson 0: Switching on Vim mode


1. Open "Edit" menu and make sure that "Enable Vim mode" checkbox
   is checked. Look at top-right corner of your screen.
   You'll see a green rounded rectangle.

2. If the rectangle is not green, set focus to the editor widget
   and press <ESC> a few times.

3. Now, make sure that your Shift-Lock key is NOT depressed and press
   the   j   key enough times to move the cursor so that Lesson 1.1
   completely fills the screen.

NOTE: If you don't like the Vim mode you always can switch it off
in the `Edit` menu. But Enki hopes you'll like it.



-----------------------------------------------------------------------------
## Lesson 1.1: Moving the cursor


   ** To move the cursor, press the h,j,k,l keys as indicated. **
```
hjkl
<v^>
```

Hint:  The *h* key is at the left and moves left.
Hint:  The *l* key is at the right and moves right.
Hint:  The *j* key looks like a down arrow.

  1. Move the cursor around the screen until you are comfortable.

  2. Hold down the down key (j) until it repeats.
     Now you know how to move to the next lesson.

  3. Using the down key, move to Lesson 1.2.

NOTE: If you are ever unsure about something you typed, press <ESC> to place
      you in Normal mode.  Then retype the command you wanted.

NOTE: The cursor keys should also work.  But using hjkl you will be able to
      move around much faster, once you get used to it.  Really!



-----------------------------------------------------------------------------
## Lesson 1.2: Text editing - Deletion


** Press  x  to delete the character under the cursor. **

  1. Move the cursor to the line below marked --->.

  2. To fix the errors, move the cursor until it is on top of the
     character to be deleted.

  3. Press the    x  key to delete the unwanted character.

  4. Repeat steps 2 through 4 until the sentence is correct.

      ---> The ccow jumpedd ovverr thhe mooon.

  5. Now that the line is correct, go on to Lesson 1.3.

NOTE: As you go through this tutor, do not try to memorize, learn by usage.



-----------------------------------------------------------------------------
## Lesson 1.3: Text editing - Insertion


** Press  i  to insert text. **

  1. Move the cursor to the first line below marked --->.

  2. To make the first line the same as the second, move the cursor on top
     of the first character AFTER where the text is to be inserted.

  3. Press  i . Rounded rectangle shall become orange and contain text 'insert'

  4. Type in the necessary additions.

  5. As each error is fixed press <ESC> to return to Normal mode.
     Repeat steps 2 through 4 to correct the sentence.

      ---> There is text misng this .
      ---> There is some text missing from this line.

  6. When you are comfortable inserting text move to lesson 1.4.



-----------------------------------------------------------------------------
## Lesson 1.4: Text editing - Appending


** Press  A  to append text. **

  1. Move the cursor to the first line below marked --->.
     It does not matter on what character the cursor is in that line.

  2. Press  A  and type in the necessary additions.

  3. As the text has been appended press <ESC> to return to Normal mode.

  4. Move the cursor to the second line marked ---> and repeat
     steps 2 and 3 to correct this sentence.

      ---> There is some text missing from th
           There is some text missing from this line.
      ---> There is also some text miss
           There is also some text missing here.



-----------------------------------------------------------------------------
## Lesson 1 Summary


  1. The cursor is moved using either the arrow keys or the hjkl keys.
     h (left)    j (down)       k (up)        l (right)

  2. To delete the character at the cursor type:  x

  3. To insert or append text type:
     i   type inserted text   <ESC>         insert before the cursor
     A   type appended text   <ESC>         append after the line

NOTE: Pressing <ESC> will place you in Normal mode or will cancel
      an unwanted and partially completed command.

Now continue with Lesson 2.



-----------------------------------------------------------------------------
## Lesson 2.1: Deletion Commands


** Type  dw  to delete a word. **

  1. Press  <ESC>  to make sure you are in Normal mode.

  2. Move the cursor to the line below marked --->.

  3. Move the cursor to the beginning of a word that needs to be deleted.

  4. Type   dw     to make the word disappear.

  NOTE: The letter  d  will appear on the last line of the screen as you type it.  Vim is waiting for you to type  w .  If you see another character than  d  you typed something wrong; press  <ESC>  and start over.
---> There are a some words fun that don't belong paper in this sentence.

  5. Repeat steps 3 and 4 until the sentence is correct and go to Lesson 2.2.



-----------------------------------------------------------------------------
## Lesson 2.2: More Deletion Commands


** Type  d$    to delete to the end of the line. **

  1. Press  <ESC>  to make sure you are in Normal mode.

  2. Move the cursor to the line below marked --->.

  3. Move the cursor to the end of the correct line (AFTER the first . ).

  4. Type    d$    to delete to the end of the line.

---> Somebody typed the end of this line twice. end of this line twice.


  5. Move on to Lesson 2.3 to understand what is happening.



-----------------------------------------------------------------------------
## Lesson 2.3: On Operators and Motions


  Many commands that change text are made from an operator and a motion.
  The format for a delete command with the  d  delete operator is as follows:

```
      d   motion
```

Where:

 * d      - is the delete operator.
 * motion - is what the operator will operate on (listed below).

A short list of motions:

* w - until the start of the next word, EXCLUDING its first character.
* e - to the end of the current word, INCLUDING the last character.
* $ - to the end of the line, INCLUDING the last character.

  Thus typing  de  will delete from the cursor to the end of the word.

NOTE:  Pressing just the motion while in Normal mode without an operator will
       move the cursor as specified.



-----------------------------------------------------------------------------
## Lesson 2.4: Using a Count for a Motion


   ** Typing a number before a motion repeats it that many times. **

  1. Move the cursor to the start of the line marked ---> below.

  2. Type  2w  to move the cursor two words forward.

  3. Type  3e  to move the cursor to the end of the third word forward.

  4. Type  0  (zero) to move to the start of the line.

  5. Repeat steps 2 and 3 with different numbers.

---> This is just a line with words you can move around in.

  6. Move on to Lesson 2.5.



-----------------------------------------------------------------------------
## Lesson 2.5: Using a Count to Delete More


** Typing a number with an operator repeats it that many times. **

  In the combination of the delete operator and a motion mentioned above you
  insert a count before the motion to delete more:
```
     d   number   motion
```

  1. Move the cursor to the first UPPER CASE word in the line marked --->.

  2. Type  d2w  to delete the two UPPER CASE words

  3. Repeat steps 1 and 2 with a different count to delete the consecutive
     UPPER CASE words with one command

--->  this ABC DE line FGHI JK LMN OP of words is Q RS TUV cleaned up.



-----------------------------------------------------------------------------
## Lesson 2.6: Operating on Lines


** Type  dd   to delete a whole line. **

  Due to the frequency of whole line deletion, the designers of Vi decided
  it would be easier to simply type two d's to delete a line.

  1. Move the cursor to the second line in the phrase below.
  2. Type  dd  to delete the line.
  3. Now move to the fourth line.
  4. Type   2dd   to delete two lines.

--->  1)  Roses are red,
--->  2)  Mud is fun,
--->  3)  Violets are blue,
--->  4)  I have a car,
--->  5)  Clocks tell time,
--->  6)  Sugar is sweet
--->  7)  And so are you.



-----------------------------------------------------------------------------
## Lesson 2.7: The Undo Command


** Press  u    to undo the last commands,   U  to redo the changes. **

  1. Move the cursor to the line below marked ---> and place it on the
     first error.
  2. Type  x  to delete the first unwanted character.
  3. Now type  u  to undo the last command executed.
  4. Now press U to redo the last command.

      ---> Fiix the errors oon thhis line and reeplace them witth undo.

  5. These are very useful commands.  Now move on to the Lesson 2 Summary.



-----------------------------------------------------------------------------
## Lesson 2 Summary


  1. To delete from the cursor up to the next word type:    dw
  2. To delete from the cursor to the end of a line type:    d$
  3. To delete a whole line type:    dd

  4. To repeat a motion prepend it with a number:   2w
  5. The format for a change command is:
               operator   [number]   motion
     where:
       * operator - is what to do, such as  d  for delete
       * [number] - is an optional count to repeat the motion
       * motion   - moves over the text to operate on, such as  w (word), $ (to the end of line), etc.

  6. To move to the start of the line use a zero:  0

  7. To undo previous actions, type:            u  (lowercase u)
     To undo the undo's, type:                  U  (uppercase u)



-----------------------------------------------------------------------------
## Lesson 3.1: The Paste Command


NOTE: Original Vim calls this command "Put", but for the Enki users it is more
habitual to think about it as "Paste".

** Type  p  to paste previously deleted text after the cursor. **

  1. Move the cursor to the first ---> line below.

  2. Type  dd  to delete the line and store it in a Vim register.

  3. Move the cursor to the c) line, ABOVE where the deleted line should go.

  4. Type  p  to paste the line below the cursor.

  5. Repeat steps 2 through 4 to paste all the lines in correct order.

---> d) Can you learn too?
---> b) Violets are blue,
---> c) Intelligence is learned,
---> a) Roses are red,



-----------------------------------------------------------------------------
## Lesson 3.2: The Replace Command


** Type  rx  to replace the character at the cursor with  x . **

  1. Move the cursor to the first line below marked --->.

  2. Move the cursor so that it is on top of the first error.

  3. Type   r    and then the character which should be there.

  4. Repeat steps 2 and 3 until the first line is equal to the second one.

      --->  Whan this lime was tuoed in, someone presswd some wrojg keys!
      --->  When this line was typed in, someone pressed some wrong keys!

  5. Now move on to Lesson 3.3.

NOTE: Remember that you should be learning by doing, not memorization.



-----------------------------------------------------------------------------
## Lesson 3.3: The Change Operator


** To change until the end of a word, type  ce . **

  1. Move the cursor to the first line below marked --->.

  2. Place the cursor on the  u  in  lubw.

  3. Type  ce  and the correct word (in this case, type  ine ).

  4. Press <ESC> and move to the next character that needs to be changed.

  5. Repeat steps 3 and 4 until the first sentence is the same as the second.

---> This lubw has a few wptfd that mrrf changing usf the change operator.
---> This line has a few words that need changing using the change operator.

Notice that  ce  deletes the word and places you in Insert mode.



-----------------------------------------------------------------------------
## Lesson 3.4: More Changes Using c


** The change operator is used with the same motions as delete. **

  1. The change operator works in the same way as delete.  The format is:

      ```
               c    [number]   motion
      ```

  2. The motions are the same, such as   w (word) and  $ (end of line).

  3. Move to the first line below marked --->.

  4. Move the cursor to the first error.

  5. Type  c$  and type the rest of the line like the second and press <ESC>.

---> The end of this line needs some help to make it like the second.
---> The end of this line needs to be corrected using the  c$  command.

NOTE:  You can use the Backspace key to correct mistakes while typing.



-----------------------------------------------------------------------------
## Lesson 3 SUMMARY


  1. To paste back text that has just been deleted, type   p .
     This pastes the deleted text AFTER the cursor (if a line was deleted it
     will go on the line below the cursor).

  2. To replace the character under the cursor, type   r   and then the
     character you want to have there.

  3. The change operator allows you to change from the cursor to where the
     motion takes you.  eg. Type  ce  to change from the cursor to the end of
     the word,  c$  to change to the end of a line.

  4. The format for change is:

      ```
           c   [number]   motion
      ```

Now go on to the next lesson.



-----------------------------------------------------------------------------
## Lesson 4.1: Cursor Location


** Type  G  to move to a line in the file. **

  NOTE: Read this entire lesson before executing any of the steps!!

   1.  Remember the current line number for Step 3.

      NOTE:  You may see the cursor position in the lower right corner of the screen
             This happens when the 'ruler' option is set (see  :help 'ruler'  )

  2. Press  G  to move you to the bottom of the file.
     Type  gg  to move you to the start of the file.

  3. Type the number of the line you were on and then  G .  This will
     return you to the line you were on at the beginning of the lesson.

  4. If you feel confident to do this, execute steps 1 through 3.



-----------------------------------------------------------------------------
## Lesson 4.2: Matching Parentheses Search


 ** Type  %  to find a matching ),], or } . **

  1. Place the cursor on any (, [, or { in the line below marked --->.

  2. Now type the  %  character.

  3. The cursor will move to the matching parenthesis or bracket.

  4. Type  %  to move the cursor to the other matching bracket.

  5. Move the cursor to another (,),[,],{ or } and see what  %  does.

---> This ( is a test line with ('s, ['s ] and {'s } in it. ))


NOTE: This is very useful in debugging a program with unmatched parentheses!



-----------------------------------------------------------------------------
## Lesson 4 SUMMARY


  1. CTRL-G  displays your location in the file and the file status.
             G  moves to the end of the file.
     number  G  moves to that line number.
            gg  moves to the first line.

  2. Typing  /    followed by a phrase searches FORWARD for the phrase.
     Typing  ?    followed by a phrase searches BACKWARD for the phrase.
     After a search type  n  to find the next occurrence in the same direction
     or  N  to search in the opposite direction.
     CTRL-O takes you back to older positions, CTRL-I to newer positions.

  3. Typing  %    while the cursor is on a (,),[,],{, or } goes to its match.



-----------------------------------------------------------------------------
## Lesson 5.1: The Append Command


** Type  a  to insert text AFTER the cursor. **

  1. Move the cursor to the start of the line below marked --->.

  2. Press  e  until the cursor is on the end of  li .

  3. Type an  a  (lowercase) to append text AFTER the cursor.

  4. Complete the word like the line below it.  Press <ESC> to exit Insert
     mode.

  5. Use  e  to move to the next incomplete word and repeat steps 3 and 4.

---> This li will allow you to pract appendi text to a line.
---> This line will allow you to practice appending text to a line.

NOTE:  a, i and A all go to the same Insert mode, the only difference is where
       the characters are inserted.



-----------------------------------------------------------------------------
## Lesson 5.2: Another Way to Replace


** Type a capital  R  to replace more than one character. **

  1. Move the cursor to the first line below marked --->.  Move the cursor to
     the beginning of the first  xxx .

  2. Now press  R  and type the number below it in the second line, so that it
     replaces the xxx .

  3. Press <ESC> to leave Replace mode.  Notice that the rest of the line
     remains unmodified.

  4. Repeat the steps to replace the remaining xxx.

---> Adding 123 to xxx gives you xxx.
---> Adding 123 to 456 gives you 579.

NOTE:  Replace mode is like Insert mode, but every typed character deletes an
       existing character.



-----------------------------------------------------------------------------
## Lesson 5.3: Copy and Paste Text


** Use the  y  operator to copy text and  p  to paste it **

  1. Go to the line marked with ---> below and place the cursor after "a)".

  2. Start Visual mode with  v  and move the cursor to just before "first".

  3. Type  y  to yank (copy) the highlighted text.

  4. Move the cursor to the end of the next line:  j$

  5. Type  p  to put (paste) the text.  Then type:  a second <ESC> .

  6. Use Visual mode to select " item.", yank it with  y , move to the end of
     the next line with  j$  and put the text there with  p .

```
--->  a) this is the first item.
      b)
```

  NOTE: you can also use  y  as an operator;  yw  yanks one word.



-----------------------------------------------------------------------------
## Lesson 5 Summary


  1. Type  o  to open a line BELOW the cursor and start Insert mode.
     Type  O  to open a line ABOVE the cursor.

  2. Type  a  to insert text AFTER the cursor.
     Type  A  to insert text after the end of the line.

  3. The  e  command moves to the end of a word.

  4. The  y  operator yanks (copies) text,  p  puts (pastes) it.

  5. Typing a capital  R  enters Replace mode until  <ESC>  is pressed.


-----------------------------------------------------------------------------
  This concludes the Vim mode Tutor.  It was intended to give a brief overview of the Vim mode, just enough to allow you to use the mode fairly easily.
  Check the [documentation](https://github.com/hlamer/enki/wiki/Vim) to find many more useful commands.

  This tutorial is based on original Vim tutorial by Michael C. Pierce and Robert K. Ware, Colorado School of Mines using ideas supplied by Charles Smith, Colorado State University. E-mail: bware@mines.colorado.edu.

  Modified for Vim by Bram Moolenaar.

  Modified for Enki by Andrei Kopats.

-----------------------------------------------------------------------------
