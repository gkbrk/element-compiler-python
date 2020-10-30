#!/usr/bin/env python3

# element-compiler-python: Web component to JS compiler
# Copyright (C) 2020  Gokberk Yaltirakli
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.

"""Web component compiler

This script implements a small compiler for web components / custom
elements. The compiler reads Vue-style single-file components and outputs
vanilla JS code.

This compiler is meant to be used with the Closure JS optimizer. While it
produces working code on its own, Closure makes it much smaller.

"""

from bs4 import BeautifulSoup, NavigableString
import json
import re
import subprocess
import sys

# TODO: Output jsdoc type hints for Closure compiler
# TODO: Compiler flags to customize behaviour

def sassc_available():
    """Checks if the `sassc` executable is available on the system

    Tries to execute `sassc` and checks the return code to see if it is
    available on the system.

    Returns
    -------
    bool
        The availability of the SASS compiler in the system

    """

    try:
        res = subprocess.run(["sassc", "-h"], capture_output=True)
        return res.returncode == 0
    except:
        return False


def sassc(style):
    """Compile a SASS stylesheet into minified CSS

    This function compiles SASS using the `sassc` executable.

    Parameters
    ----------
    style : str
        SASS stylesheet

    Returns
    -------
    str
        Minified CSS

    """

    style = style.encode("utf-8")
    return (
        subprocess.run(
            ["sassc", "-s", "-t", "compressed"],
            input=style,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )


# If sassc is not available, return unminified stylesheet
if not sassc_available():
    sassc = lambda x: x.strip()


def js_str_esc(s):
    """Escape a string in order to be embedded in JS code

    Replaces problematic charactes in a string with their escape sequences.

    Parameters
    ----------
    s : str
        The string to escape

    Returns
    -------
    str
        Escaped string

    """
    res = ""

    for c in s:
        if c == "'":
            res += "\\'"
        elif c == "\n":
            res += "\\n"
        elif c == "\\":
            res += "\\\\"
        else:
            res += c

    return res


def out(*t):
    """Outputs arguments without any spacing or newlines"""
    print("".join(t), end="")


def html2js(tag):
    """Compile HTML tags into Javascript DOM elements

    This function compiles a BeautifulSoup HTML element recursively, and outputs
    JS code that creates DOM elements using the `$e` helper.

    Please note that this function outputs to stdout directly, and returns None.

    Parameters
    ----------
    tag : bs4.Element
        The HTML element to compile to JS

    Returns
    -------
    None

    """
    if isinstance(tag, NavigableString):
        out('"', js_str_esc(tag.string), '"')
        return

    out("$e('")
    out(js_str_esc(tag.name))
    out("',{")

    for key in tag.attrs:
        val = tag[key]
        if key == "class":
            key = "classList"
        out(f"'{js_str_esc(key)}':'{js_str_esc(val)}',")
    out("},[")

    for tag in tag.children:
        html2js(tag)
        out(",")

    out("])")


def parse_properties(src):
    """Parse properties from HTML comments

    Parses property key/value pairs from HTML comments. After encountering an
    empty line, the parsing stops. For each HTML comment before that, the first
    word becomes the property name and the rest becomes the value.

    Parameters
    ----------
    src : str
        Component file contents

    Returns
    -------
    Dictionary
        Properties and their values

    """
    properties = {}

    for line in src.split("\n\n", 2)[0].split("\n"):
        prop = re.match("^<!-- (\w*?) (.*?) -->$", line)
        if prop:
            properties[prop.group(1)] = prop.group(2)

    return properties


def compile(src):
    """Compile a web component to Javascript

    This function takes in the contents of a single-file web component file, and
    outputs the JS customElements definition.

    Parameters
    ----------
    src : str
        Component file contents

    """
    soup = BeautifulSoup(src, "html.parser")

    properties = parse_properties(src)

    tpl = soup.find_all("template")
    assert len(tpl) == 1
    tpl = tpl[0]

    style = ""

    for s in soup.find_all("style"):
        style += s.decode_contents().strip()

    attributes = set()

    for s in soup.find_all("script", event="attr"):
        attributes.add(s["attr"])

    out(f"customElements.define('{properties['name']}',")
    out("class extends HTMLElement{")

    out("constructor(){")
    out("super();")
    out("this.shadow = this.attachShadow({'mode':'open'});")

    if style:
        style = sassc(style)
        out("this.shadow.append($e('style', {}, ['")
        out(js_str_esc(style))
        out("']));")

    for t in tpl:
        out("this.shadow.append(")
        html2js(t)
        out(");")

    for s in soup.find_all("script", event="constructor"):
        out(s.decode_contents())

    out("}")

    if attributes:
        out("static get observedAttributes(){return")
        out(json.dumps(sorted(list(attributes))))
        out(";}")

    if soup.find("script", event="connected"):
        out("connectedCallback(){")

        for s in soup.find_all("script", event="connected"):
            out(s.decode_contents())

        out("}")

    if soup.find("script", event="disconnected"):
        out("disconnectedCallback(){")

        for s in soup.find_all("script", event="disconnected"):
            out(s.decode_contents())

        out("}")

    for getter in soup.find_all("script", event="getter"):
        out("get ", getter["name"], "(){")
        out(getter.decode_contents())
        out("}")

    for setter in soup.find_all("script", event="setter"):
        out("set ", setter["name"], "(value){")
        out(setter.decode_contents())
        out("}")

    if attributes:
        out("attributeChangedCallback(__attrName, oldValue, value){")
        for s in soup.find_all("script", event="attr"):
            out("if (__attrName === '", js_str_esc(s["attr"]), "'){")
            out(s.decode_contents())
            out("}")
        out("}")

    out("});")


# Built-in helper to create HTML elements in Javascript
out(
    """let $e = (t,p={},c=[]) => {
  let el=document.createElement(t);
  Object.assign(el,p);
  el.append(...c);
  return el;
};"""
)

for p in sys.argv[1:]:
    with open(p) as p:
        compile(p.read())
