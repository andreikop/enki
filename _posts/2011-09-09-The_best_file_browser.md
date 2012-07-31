---
layout: post
title: The best file browser
baseurl: ../../../
---


Some time ago I noticed, that I dislike our File Browser ui. It takes too lot of free space, and there are too lot of buttons, but I never use them.
I decided to improve the UI...

Here is old version:

<img src="../../../blog-screens/old-file-browser.png"/>

###Useless functionality

At first, I just removed 2 of the buttons.

Why do we need "Select a root folder", if it only opens file dialogue, similar to main UI? I think, we don't need it. **Removed**

Do we need _Set selected item as root_ button? If I am browsing with a mouse, I don't select item, than click the button, I just doubleclick the item. If I am browsing with keyboard, I also don't click the button, I press enter on the item. **Removed**

Do you use bookmarks in the current File Browser version? This functionality intended to help us quickly open popular directories, but I'm to lazy for keeping directories list up to date, therefore, don't use bookmarks. Functionality does not serve its goal. Useless. **Removed**

OK, it seems I removed all, now UI contains only 1 button (Up), one read only edit box and the tree. As simple, as possible. Now about useful functionality...

###Better navigation

Let's look at popular web browsers. It is kind of software, which actively used at most every PC user. Really big user base, and valuable experience.

How do you open your pages? I think:

1. Type a address
2. Click a link
3. Start to type a address, and browser completes it for you, according to your history
4. Press Back and Forward

I think, all 4 variants are suitable for a text editor File Browser as well. So, my changes are:

1. Now edit line are editable, and it completes your path with file system completer.
2. Already was done. Doubleclick a directory to open it, or press Enter
3. This is replacement of old bookmarks. Now File Browser remembers your history and allows you select your most popular directories (not the last ones, but the most popular!) in the combo
4. Now Back directory is available as combo item. Some other editors allow you to go back to your previous directory, but, I think, it is useless, you always can press "Up" or select visible directory in the tree. Our file browser allows you to jump back to previous directory, where file has been opened. I think, it is more useful.
5. jump to directory of current file. Now it is also available as a combo item.


I'm also thinking about adding web browser like Back and Forward buttons to the dock title, and, probably, _Go to directory of current file_ button, so, combo will contain only popular dirrectories.

So, I think, here is the best text editor File Browser:

<span>
    <img src="../../../blog-screens/new-file-browser-2.png"/><br/><br/>
    <img src="../../../blog-screens/new-file-browser.png"/>
</span>


Of course, I'm trolling you with this _the best_. Try to argue, that it is possible to do even better ;)

Now this file browser included to enki. But, it is not released yet, only available as sources.
