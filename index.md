---
layout: default
title: mksv3. Code editor
root: .
---


# mksv3

###Code editor


* **User friendly.** Intuitive interface. Works out of the box. You don't have to read a lot of docs
* **Hacker friendly**. Code as quickly as possible. Without mouse.
* **Minimalistic interface**. Screen is used for code, not for bells and whistles.
* **High quality**. No long list of fancy features. But, what is done, is done well.
* **Extensible.** Missing feature or language support? Don't create a new IDE, create a plugin

See [Features](features.html) and [Why new code editor?](why-new.html)
    
<table frame="void">
    <tr>
        <td width="20%">
            <a href="screenshots/main-ui.png">
                <img src="screenshots/preview/main-ui.png" width="100%" height="100%"/>
            </a>
            UI
        </td>
        <td width="20%">
            <a href="screenshots/minimal.png">
                <img src="screenshots/preview/minimal.png" width="100%" height="100%"/>
            </a>
            Minimalistic UI
        </td>
        <td width="20%">
            <a href="screenshots/search.png">
                <img src="screenshots/preview/search.png" width="100%" height="100%"/>
            </a>
            Search
        </td>
        <td width="20%">
            <a href="screenshots/search-replace.png">
                <img src="screenshots/preview/search-replace.png" width="100%" height="100%"/>
            </a>
            Good bye sed
        </td>
        <td width="20%">
            <a href="screenshots/markdown-preview.png">
                <img src="screenshots/preview/markdown-preview.png" width="100%" height="100%"/>
            </a>
            Markdown live preview
        </td>
    </tr>
</table>

mksv3 is **crossplatform**, but, currently has been tested only on Linux. Team will be appreciate you, if you shared your experience about other platforms.

The project is licensed under **GNU GPL v2** license


## Blog
{% for post in site.posts limit:5 %}
<div>
  {{ post.date | date_to_string }}
  <a href="{{ page.root }}{{ post.url }}">{{ post.title }}</a>
  <p>{{ post.excerpt }}</p>
</div>
{% endfor %}

<a href="archive.html">Archives</a>
