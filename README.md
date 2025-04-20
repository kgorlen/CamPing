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

**camping** - Check Blue Iris security camera status and ping healthchecks.io with results.

# SYNOPSIS

```camping```

# DESCRIPTION

The **camping** CLI logs into the Blue Iris server using the URL and user name
in the  **camping.toml** configuration file, obtains a list of cameras and their
status, and pings healthchecks.io at the URL also specified in the configuration
file. If all cameras are UP, **camping** sends a success ping; if not,
**camping** sends a /fail ping with a list of the failed cameras.

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

## blueiris_url

The `blueiris_url` can be found in Blue Iris *Settings -> Web server*.

<pre>
blueiris_url = "http://<i>IP address</i>:<i>port</i>"
</pre>

## blueiris_user

The list of valid users can be found in Blue Iris *Settings -> Users*.

```
blueiris_user = "LiveView"
```

The `blueiris_user` setting is used to retrieve the Blue Iris user's password
from the PC's keyring.  Set the Blue Iris password with the command:
<pre>
keyring set "blueiris" "<i>blueiris_user</i>"
</pre>
For example:

```
keyring set "blueiris" "LiveView"
```

## blueiris_ping_url

See [Healthchecks.io](https://healthchecks.io/about/) for details.  The
`blueiris_ping_url` is pinged with the status of the Blue Iris application: OK
if the status of all cameras is successfully retrieved, or failure is signalled
with an error message.

```
# Blue Iris status healthchecks.io URL
blueiris_ping_url = "https://hc-ping.com/**********************/blue-iris*"
```

## cameras_ping_url

The `cameras_ping_url` is pinged with the status of the cameras connected to
Blue Iris: OK if all cameras are **UP**, or failure is signalled with a list of
cameras that are **DOWN**.

```
# Camera status healthchecks.io URL
cameras_ping_url = "https://hc-ping.com/**********************/security-cameras"
```

# INSTALLATION

## PREREQUISITES

[Install python 3.12 or later version](https://www.python.org/downloads/).

Install [pipx](https://pipx.pypa.io/stable/):

```
pip install pipx
```

Install [keyring](https://pypi.org/project/keyring/):

```
pipx install keyring
```

## INSTALL **camping** FROM `.whl` package

<pre>
<code>pipx install <i>path</i>\camping-<i>version</i>-py3-none-any.whl</code>
</pre>

For example:

<pre>
<code>pipx install <i>path</i>\camping-2.0.0-py3-none-any.whl</code>
</pre>

## INSTALL **camping** FROM `.tar.gz` package

Alternatively, install **camping** from a `.tar.gz` package file:

<pre>
<code>pipx install <i>path</i>\camping-<i>version</i>.tar.gz</code>
</pre>

For example:

<pre>
<code>pipx install <i>path</i>\camping-2.0.0-.tar.gz</code>
</pre>

# SEE ALSO

* [Blue Iris](https://blueirissoftware.com/)<br>
* [pyblueiris Documentation](https://nwesterhausen.github.io/pyblueiris/index.html)<br>
* [Healthchecks.io](https://healthchecks.io/about/)<br>
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
