---
layout: home
title: Enki. A text editor for programmers
baseurl: .
---

<div class="content-row-1" markdown="1">

<h2>Enki is a text editor for programmers. It is:</h2>
<ul>
    <li><strong>User friendly.</strong> Intuitive interface. Works out of the box. You don&#8217;t have to read a lot of docs</li>
    <li><strong>Hacker friendly.</strong> Work as quickly as possible. You don&#8217;t need your mouse for coding.</li>
    <li><strong>Lighweight.</strong> Some IDEs show splashscreen. Enki will never do it. It just starts quickly.</li>
    <li><strong>Advanced.</strong> You invent software. An editor helps you to do a routine job.</li>
    <li><strong>Extensible.</strong> Operating systems are designed for running applications. Enki is designed for running plugins.</li>
    <li><strong>Cross platform.</strong> Use your habitual editor on any OS. Currently has beeen tested on Linux, MacOS X, Windows.</li>
    <li><strong>High quality.</strong> No long list of fancy features. But, what is done, is done well.</li>
    <li><strong>Open source.</strong> In GitHub we trust.</li>
</ul>

    <div id="social-buttons">
        <div id="twitter">
            <a href="https://twitter.com/EnkiEditor" class="twitter-follow-button" data-show-count="false" data-size="large" data-show-screen-name="false">Follow @EnkiEditor</a>
        </div>

        <!-- Hiding Facebook button
            <div id="facebook">
                <a href="http://www.facebook.com/sharer.php?u=http://enki-editor.org/"><img src="./img/facebook.png" title="Share enki editor on Facebook" alt="Share enki editor on Facebook"></a>
            </div>
        -->
    </div>

</div>

<div id="content-row-2">
    <div id="download">

        <div>
            <a href="install-sources.html" class="download-button">
                <img src="../img/tgz.png"/>
                <br/>
                Source<br/>package
            </a>

            <a href="http://software.opensuse.org/download.html?project=home%3Ahlamer%3Aenki&amp;package=enki" class="download-button">
                <table>
                    <tr>
                        <td>
                            <img src="../img/debian.png"/>
                        </td>
                        <td>
                            <img src="../img/fedora.png"/>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <img src="../img/suse.png"/>
                        </td>
                        <td>
                            <img src="../img/ubuntu.png"/>
                        </td>
                    </tr>
                </table>
                <br/>
                Linux<br/>installer
            </a>

            <a href="http://github.com/hlamer/enki/releases" class="download-button">
                <img src="../img/win.svg" width="120" height="106" align="midle"/>
                <br/>
                Windows<br/>installer
            </a>

        </div>

        <a href="./packaging.html" id="where-is">Where is package for my OS?</a>

    </div>


    <div id="news">
        <h2>News</h2>
        <div id="news-inner-container">
            {% for post in site.posts limit:5 %}
            <div class="news-row">
                <div class="date">
                    {{ post.date | date_to_string }}
                </div>
                <div class="post-title">
                    <a href="{{ page.baseurl }}{{ post.url }}">{{ post.title }}</a>
                </div>
            </div>
            {% endfor %}
        </div>
        <div id="allnews">
            <a href="archive.html">All news...</a>
        </div>
    </div>


    <div id="seperator">
    </div>

</div>

<div id="screenshot-container">
     <div class="screenshot-row">
       <div class="screenshot">
            <a href="screenshots/minimal.png" rel="lightbox[screenshots]" title="Minimalistic UI">
                <img src="screenshots/preview/minimal.png" class="fancy-border" /></a><br />
            Minimalistic UI
        </div>
        <div class="screenshot">
            <a href="screenshots/search.png" rel="lightbox[screenshots]" title="Search">
                <img src="screenshots/preview/search.png" class="fancy-border" /></a><br />
            Search
        </div>
    </div>
    <div class="screenshot-row">
        <div class="screenshot">
            <a href="screenshots/navigator.png" rel="lightbox[screenshots]" title="Navigator">
                <img src="screenshots/preview/navigator.png" class="fancy-border" /></a><br />
            Navigator
        </div>
        <div class="screenshot">
            <a href="screenshots/markdown-preview.png" rel="lightbox[screenshots]" title="Markdown live preview">
                <img src="screenshots/preview/markdown-preview.png" class="fancy-border" /></a><br />
            Markdown live preview
        </div>
    </div>

    <!-- Hiding More Screenshots link
    <div id="more-screenshots"><a href="#">More screenshots ...</a></div>
    -->

    </div>


</div>
