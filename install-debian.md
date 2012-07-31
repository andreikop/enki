---
layout: default
title: Install enki on Debian
baseurl: .
---

# Install on Debian (and based on it)

    su
    echo 'deb http://ppa.launchpad.net/monkeystudio/ppa/ubuntu lucid main' >  \
        /etc/apt/sources.list.d/enki
    apt-get update
    apt-get install enki

### Enjoy
Don't forget to send a bug report, if you are having some problems
