<!--
Markdown Guide: https://www.markdownguide.org/basic-syntax/
-->
<!--
Disable markdownlint errors:
fenced-code-language MD040
no-inline-html MD033
-->
<!-- markdownlint-disable MD040 MD033-->

# CamPing

**camping** - Ping security cameras.

# SYNOPSIS

```camping```

# DESCRIPTION

The **camping** CLI pings the cameras listed in the **camping.toml** configuration file
and pings healthchecks.io at the URL also specified in the configuration file.
If all cameras respond, **camping** sends a success ping; if not, **camping**
sends a /fail ping with a list of the failed cameras.

**camping** also writes a log file named **camping.log** to the conventional
OS-dependent log directory, `C:\Users\`*`Username`*`\AppData\Local\CamPing\Logs`
on Windows.

# OPTIONS

None.

# **camping** SETTINGS

Settings for **camping** are configured in the **camping.toml** file in the
conventional OS-dependent data directory,
`C:\Users\`*`Username`*`\AppData\Roaming\CamPing` on Windows.

See [TOML: A config file format for humans](https://toml.io/en/) for the
**.toml** file format specification.

## healthchecks_url

```
# healthchecks.io Ping URL
healthchecks_url = "https://hc-ping.com/**********************/security-cameras"
```

## [cameras]

```
[cameras]

#Cam#        IP         Model         Name
Cam1  = ["10.0.0.8",  "Amcrest",   "Lobby"]
Cam2  = ["10.0.0.9",  "Amcrest",   "S Corridor East"]
Cam3  = ["10.0.0.11", "Amcrest",   "Garage SW"]
Cam4  = ["10.0.0.17", "Amcrest",   "Garage North"]
Cam5  = ["10.0.0.18", "Amcrest",   "Garage East"]
Cam6  = ["10.0.0.15", "Amcrest",   "Garage SE"]
Cam7  = ["10.0.0.25", "Amcrest",   "N Corridor West"]
Cam8  = ["10.0.0.12", "Amcrest",   "Garage NW"]
Cam9  = ["10.0.0.16", "Amcrest",   "Roof West"]
Cam10 = ["10.0.0.19", "Amcrest",   "Lobby Door"]
Cam11 = ["10.0.0.10", "Amcrest",   "Commercial"]
Cam12 = ["10.0.0.71", "HIKVision", "Columbus"]
Cam13 = ["10.0.0.70", "HIKVision", "Powell Entrance"]
Cam14 = ["10.0.0.72", "HIKVision", "Powell South"]
Cam15 = ["10.0.0.73", "HIKVision", "Columbus Entrance"]
Cam16 = ["10.0.0.13", "Amcrest",   "Garage Gate"]
Cam17 = ["10.0.0.24", "Amcrest",   "Roof East"]
Cam18 = ["10.0.0.14", "Amcrest",   "Mail Room"]
Cam19 = ["10.0.0.22", "Amcrest",   "S Corridor West"]
Cam20 = ["10.0.0.20", "Amcrest",   "Garage Elevator"]
Cam21 = ["10.0.0.21", "Amcrest",   "Bike Room"]
Cam22 = ["10.0.0.23", "Amcrest",   "Server Room"]
```

# INSTALLATION

## PREREQUISITES

[Install python 3.12 or later version](https://www.python.org/downloads/).

Install [pipx](https://pipx.pypa.io/stable/):

```
pip install pipx
```

## INSTALL **camping** FROM `.whl` package

<pre>
<code>pipx install <i>path</i>\camping-<i>version</i>-py3-none-any.whl</code>
</pre>

For example:

<pre>
<code>pipx install <i>path</i>\camping-0.1.5-py3-none-any.whl</code>
</pre>

## INSTALL **camping** FROM `.tar.gz` package

Alternatively, install **camping** from a `.tar.gz` package file:

<pre>
<code>pipx install <i>path</i>\camping-<i>version</i>.tar.gz</code>
</pre>

For example:

<pre>
<code>pipx install <i>path</i>\camping-0.1.5-.tar.gz</code>
</pre>

# SEE ALSO

* [tcppinglib: Easy Way to Measure Connectivity and Latency](https://pypi.org/project/tcppinglib/)<br>
* [TOML: A config file format for humans](https://toml.io/en/)<br>

# AUTHOR

Keith Gorlen<br>
<kgorlen@gmail.com>

# COPYRIGHT

Copyright 2025 Keith Gorlen

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
