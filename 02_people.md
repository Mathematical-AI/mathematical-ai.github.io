---
layout: page
title: People
permalink: /people/
---

{% assign people = site.people | where: "position-tag", "professor" %}
{% if people.size > 0 %}
# Academic Staff
{% for person in people %}
[{{ person.title }}]({{ person.url | relative_url }})
{% endfor %}
{% endif %}

{% assign people = site.people | where: "position-tag", "lecturer" %}
{% if people.size > 0 %}
{% for person in people %}
[{{ person.title }}]({{ person.url | relative_url }})
{% endfor %}
{% endif %}

{% assign people = site.people | where: "position-tag", "postdoc" %}
{% if people.size > 0 %}
# Research Staff
{% for person in people %}
[{{ person.title }}]({{ person.url | relative_url }})
{% endfor %}
{% endif %}

{% assign people = site.people | where: "position-tag", "phd-student" %}
{% if people.size > 0 %}
# PhD Students
{% for person in people %}
[{{ person.title }}]({{ person.url | relative_url }})
{% endfor %}
{% endif %}