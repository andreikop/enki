---
layout: home
title: Enki. A text editor for programmers
baseurl: .
---

<div class="content-row-1" markdown="1">

<h2>Enki is a text editor for programmers. It is:</h2>
<ul>
    <li><strong>User friendly.</strong> Intuitive interface. Works out of the box. You don&#8217;t have to read a lot of docs.</li>
    <li><strong>Hacker friendly.</strong> Work as quickly as possible. Navigate efficiently without your mouse.</li>
    <li><strong>Advanced.</strong> You invent software. An editor helps you focus on inventing, instead of fighting with your tools.</li>
    <li><strong>Extensible.</strong> Operating systems are designed for running applications. Enki is designed for running plugins.</li>
    <li><strong>Cross platform.</strong> Use your habitual editor on any OS. Tested on Linux and Windows. Users report that Enki works Mac OS X.</li>
    <li><strong>High quality.</strong> No long list of fancy features. But, what is done, is done well.</li>
    <li><strong>Open source.</strong> Created, tested, and designed for the community, by the community, and with the community.</li>
</ul>

<!-- Hiding social buttons
    <div id="social-buttons">
        <div id="twitter">
            <a href="https://twitter.com/EnkiEditor" class="twitter-follow-button" data-show-count="false" data-size="large" data-show-screen-name="false">Follow @EnkiEditor</a>
        </div>

            <div id="facebook">
                <a href="http://www.facebook.com/sharer.php?u=http://enki-editor.org/"><img src="./img/facebook.png" title="Share enki editor on Facebook" alt="Share enki editor on Facebook"></a>
            </div>
    </div>
-->

</div>

<div id="content-row-2">
    <div id="download">

        <div>
            <a href="https://github.com/andreikop/enki/#installation" class="download-button">
                <img src="../img/tgz.png"/>
                <br/>
                Source<br/>package
            </a>

            <a href="http://software.opensuse.org/download.html?project=home%3Ahlamer%3Aenki&amp;package=enki" class="download-button">
                <table valign="center">
                    <tr>
                        <td>
                            <img src="../img/debian.png" width="48" height="48"/>
                        </td>
                        <td>
                            <img src="../img/fedora.png" width="48" height="48"/>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <img src="../img/ubuntu.png" width="48" height="48"/>
                        </td>
                        <td>
                            <img src="../img/suse.png" width="48" height="48"/>
                        </td>
                    </tr>
                </table>
                <br/>
                Linux<br/>installer
            </a>

            <a href="http://github.com/andreikop/enki/releases" class="download-button">
                <img src="../img/win.svg" width="110" height="110"/>
                <br/>
                Windows<br/>installer
            </a>

        </div>

        <a href="./packaging.html" id="where-is">Where is the package for my OS?</a>

    </div>


    <div id="news">
        <h2>News</h2>
        <div id="news-inner-container">
            {% for post in site.posts limit:6 %}
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
            <a href="screenshots/minimalistic.png" rel="lightbox[screenshots]" title="Minimalistic UI. Really">
                <img src="screenshots/preview/minimalistic.png" class="fancy-border" /></a><br />
            Truly Minimalistic UI
        </div>
        <div class="screenshot">
            <a href="screenshots/search.png" rel="lightbox[screenshots]" title="Best in class search-replace functionality">
                <img src="screenshots/preview/search.png" class="fancy-border" /></a><br />
            Best-in-class search/replace functionality
        </div>
    </div>
    <div class="screenshot-row">
        <div class="screenshot">
            <a href="screenshots/navigator.png" rel="lightbox[screenshots]" title="In-file navigation for 40+ languages">
                <img src="screenshots/preview/navigator.png" class="fancy-border" /></a><br />
            In-file navigation for 40+ languages
        </div>
        <div class="screenshot">
            <a href="screenshots/markdown-preview.png" rel="lightbox[screenshots]" title="Markdown, HTML, reStructuredText live preview">
                <img src="screenshots/preview/markdown-preview.png" class="fancy-border" /></a><br />
            Markdown, HTML, reStructuredText live preview
        </div>
    </div>

    <div class="screenshot-row">
        <div class="screenshot">
            <a href="screenshots/locator.png" rel="lightbox[screenshots]" title="Fuzzy file-matching and bash-like path completion">
                <img src="screenshots/preview/locator.png" class="fancy-border" /></a><br />
            Fuzzy file-matching and bash-like path completion
        </div>
        <div class="screenshot">
            <a href="screenshots/repl.png" rel="lightbox[screenshots]" title="REPL for Python, SML, Scheme">
                <img src="screenshots/preview/repl.png" class="fancy-border" /></a><br />
            REPL for Python, SML, Scheme
        </div>
    </div>

    <div class="screenshot-row">
        <div class="screenshot">
            <a href="screenshots/pylint.png" rel="lightbox[screenshots]" title="Flake8 support">
                <img src="screenshots/preview/pylint.png" class="fancy-border" /></a><br />
            Pylint support
        </div>
        <div class="screenshot">
            <a href="screenshots/vim.png" rel="lightbox[screenshots]" title="Vim mode">
                <img src="screenshots/preview/vim.png" class="fancy-border" /></a><br />
            Vim mode
        </div>
    </div>

    <!-- Hiding More Screenshots link
        <div id="more-screenshots"><a href="#">More screenshots ...</a></div>
    -->

</div>
