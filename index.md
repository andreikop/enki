---
layout: default
title: mksv3. Code editor
root: .
---


# mksv3

mksv3 is a text editor for programmers. It is:


* **User friendly.** Intuitive interface. Works out of the box. You don't have to read a lot of docs
* **Hacker friendly.** Code as quickly as possible. Without mouse.
* **Lighweight.** Some IDEs show splashscreen. mksv3 will never do it. It just starts quickly.
* **Extensible.** Operating systems are designer for running applications. MkS is designed for running plugins.
* **High quality.** No long list of fancy features. But, what is done, is done well.
* **Open source.** This is our religion.

<a href="https://twitter.com/AndreiKopats" class="twitter-follow-button" data-show-count="false" data-size="large" data-show-screen-name="false">Follow @AndreiKopats</a>

##Download
<ul>
    <li>
        <a href="install-sources.html">Sources</a>
    </li>
    <li>
        <a href="install-ubuntu.html">Ubuntu package</a>
    </li>
    <li>
        <a href="install-debian.html">Debian package</a>
    </li>
</ul>

<table frame="void">
    <tr>
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


## News
{% for post in site.posts limit:5 %}
<div>
  {{ post.date | date_to_string }}
  <a href="{{ page.root }}{{ post.url }}">{{ post.title }}</a>
  <p>{{ post.excerpt }}</p>
</div>
{% endfor %}

<a href="archive.html">All news...</a>
