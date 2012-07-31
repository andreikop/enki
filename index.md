---
layout: home
title: Enki. Code editor
baseurl: .
---

<!--[if lte IE 7]>
  <link rel="stylesheet" type="text/css" href="{{ page.baseurl }}/css/ie7index.css">
  <![endif]-->

<div class="content-row-1" markdown="1">
##enki is a text editor for programmers. It is:

* **User friendly.** Intuitive interface. Works out of the box. You don't have to read a lot of docs
* **Hacker friendly** Code as quickly as possible. Without mouse.
* **Lighweight.** Some IDEs show splashscreen. enki will never do it. It just starts quickly.
* **Extensible.** Operating systems are designed for running applications. MkS is designed for running plugins.
* **High quality.** No long list of fancy features. But, what is done, is done well.
* **Open source.** This is our religion.

    <div id="social-buttons">
        <div id="twitter">
            <a href="https://twitter.com/AndreiKopats" class="twitter-follow-button" data-show-count="false" data-size="large" data-show-screen-name="false">Follow @AndreiKopats</a>
        </div>

    <!-- Hiding Facebook button
        <div id="facebook">
            <a href="http://www.facebook.com/sharer.php?u=http://hlamer.github.com/mksv3/"><img src="./img/facebook.png" title="Share enki editor on Facebook" alt="Share enki editor on Facebook"></a>
        </div>
        -->
    
    </div>
</div>

<div id="content-row-2">
    <div id="left-col">


        <div id="download">
            
            <h2>Download</h2>
            
            <div><a id="source-button" href="install-sources.html">Source Package</a></div>
            
            <div><a id="ubuntu-button" href="install-ubuntu.html">Ubuntu Package</a></div>

            <div><a id="debian-button" href="install-debian.html">Debian Package</a></div>

       
    <!-- Hiding unused download buttons

    <div><a id="macos-button" href="install-macos.html">MacOS Package</a></div>

    <div><a id="windows-button" href="install-windows.html">Windows Package</a></div>

    <div id="more-downloads"><a href="#">More downloads ...</a></div>
    -->


        </div>
          

        <div id="news">
            <h2>News</h2>
            <div id="news-inner-container">
                <div id="dates">
                    {% for post in site.posts limit:5 %}
                    <div>
                    {{ post.date | date_to_string }}
                    </div>
                    {% endfor %}
                </div>
                
                <div id="posts">
                    {% for post in site.posts limit:5 %}
                    <div>
                    <a href="{{ page.baseurl }}{{ post.url }}">{{ post.title }}</a>
                    {{ post.excerpt }}
                    </div>
                    {% endfor %}
                </div>
            </div>
            <br />
            <div id="allnews">
                <a href="archive.html">All news...</a>
            </div>

        </div>
    </div>


<div id="screenshot-container">
     <div class="screenshot-row">
       <div class="screenshot">
            <a href="screenshots/minimal.png">
                <img src="screenshots/preview/minimal.png"/></a><br />
            Minimalistic UI
        </div>
        <div class="screenshot">
            <a href="screenshots/search.png">
                <img src="screenshots/preview/search.png"/></a><br />
            Search
        </div>
    </div>
    <div class="screenshot-row">
        <div class="screenshot">
            <a href="screenshots/search-replace.png">
                <img src="screenshots/preview/search-replace.png"/></a><br />
            Good bye sed
        </div>
        <div class="screenshot">
            <a href="screenshots/markdown-preview.png">
                <img src="screenshots/preview/markdown-preview.png"/></a><br />
            Markdown live preview
        </div>
    </div>
    
    <!-- Hiding More Screenshots link
    <div id="more-screenshots"><a href="#">More screenshots ...</a></div>
    -->
    
    </div>

    <div id="seperator">
    </div>

</div>