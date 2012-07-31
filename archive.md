---
layout: default
title: Blog archives
baseurl: .
---

# {{ page.title }}

<ul>
  {% for post in site.posts %}
    {% unless post.next %}
      <h1>{{ post.date | date: '%Y' }}</h1>
    {% else %}
      {% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
      {% capture nyear %}{{ post.next.date | date: '%Y' }}{% endcapture %}
      {% if year != nyear %}
        <br/>
        <h1>{{ post.date | date: '%Y' }}</h1>
      {% endif %}
    {% endunless %}
    <li>
        {{ post.date | date_to_string }}
        <a href="{{ page.baseurl }}/{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
