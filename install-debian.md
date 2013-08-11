---
layout: default
title: Install Enki on Debian
baseurl: .
---

# Install on Debian (and based on it)

    su
    echo 'deb http://ppa.launchpad.net/hlamer/enki/ubuntu precise main' >  \
        /etc/apt/sources.list.d/enki.list
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 33DF07F5
    apt-get update
    apt-get install enki

### Enjoy
Don't forget to send a bug report, if you are having some problems
