# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB
from __future__ import absolute_import, division, print_function

import os

import json
import pytest
from six import iteritems

from ramlfications import loader
from ramlfications.errors import LoadRAMLError

from .base import EXAMPLES


def dict_equal(dict1, dict2):
    for k, v1 in list(iteritems(dict1)):
        assert k in dict2
        v2 = dict2[k]
        assert v1 == v2
    return True


def test_load_file():
    raml_file = os.path.join(EXAMPLES + "base-includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        expected_data = {
            'external': {
                'propertyA': 'valueA',
                'propertyB': 'valueB'
            },
            'foo': {
                'foo': 'FooBar',
                'bar': 'BarBaz'
            },
            'title': 'GitHub API Demo - Includes',
            'version': 'v3'
        }

        assert dict_equal(raml, expected_data)


def test_load_file_with_nested_includes():
    raml_file = os.path.join(EXAMPLES + "nested-includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        expected_data = {
            'include_one': {
                'external': {
                    'propertyA': 'valueA',
                    'propertyB': 'valueB'
                },
                'foo': {
                    'foo': 'FooBar',
                    'bar': 'BarBaz'
                },
                'not_yaml': "This is just a string.\n",
            },
            'title': 'GitHub API Demo - Includes',
            'version': 'v3'
        }

        assert dict_equal(raml, expected_data)


def test_load_file_with_nonyaml_include():
    raml_file = os.path.join(EXAMPLES + "nonyaml-includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        expected_data = {
            'not_yaml': "This is just a string.\n",
            'title': 'GitHub API Demo - Includes',
            'version': 'v3'
        }

        assert dict_equal(raml, expected_data)


def test_load_string():
    raml_str = ("""
                - foo
                - bar
                - baz
                """)
    raml = loader.RAMLLoader().load(raml_str)

    expected_data = ["foo", "bar", "baz"]
    assert raml.sort() == expected_data.sort()


def test_yaml_parser_error():
    raml_obj = os.path.join(EXAMPLES, "invalid_yaml.yaml")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(open(raml_obj))
    msg = "Error parsing RAML:"
    assert msg in e.value.args[0]


def test_include_json():
    raml_file = os.path.join(EXAMPLES + "json_includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        expected_data = {
            "title": "Sample API Demo - JSON Includes",
            "version": "v1",
            "baseUri": "http://json.example.com",
            "schemas": [{
                "json": {
                    "name": "foo",
                    "false": True
                },
            }],
            "/foo": {
                "displayName": "foo resource"
            }
        }
        assert dict_equal(raml, expected_data)


def test_include_xsd():
    raml_file = os.path.join(EXAMPLES + "xsd_includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        xml_raw = """<?xml version="1.0" encoding="UTF-8"?>
<root>
   <false>true</false>
   <name>foo</name>
</root>
"""

        expected_data = {
            "title": "Sample API Demo - XSD Includes",
            "version": "v1",
            "baseUri": "http://xml.example.com",
            "schemas": [{
                "xml": xml_raw,
            }],
            "/foo": {
                "displayName": "foo resource",
            },
        }
        assert dict_equal(raml, expected_data)


def test_include_markdown():
    raml_file = os.path.join(EXAMPLES + "md_includes.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)

        markdown_raw = """## Foo

*Bacon ipsum dolor* amet pork belly _doner_ rump brisket. [Cupim jerky \
shoulder][0] ball tip, jowl bacon meatloaf shank kielbasa turducken corned \
beef beef turkey porchetta.

### Doner meatball pork belly andouille drumstick sirloin

Porchetta picanha tail sirloin kielbasa, pig meatball short ribs drumstick \
jowl. Brisket swine spare ribs picanha t-bone. Ball tip beef tenderloin jowl \
doner andouille cupim meatball. Porchetta hamburger filet mignon jerky flank, \
meatball salami beef cow venison tail ball tip pork belly.

[0]: https://baconipsum.com/?paras=1&type=all-meat&start-with-lorem=1
"""

        expected_data = {
            "title": "Sample API Demo - Markdown Includes",
            "version": "v1",
            "baseUri": "http://markdown.example.com",
            "/foo": {
                "displayName": "foo resource"
            },
            "documentation": [{
                "title": "example",
                "content": markdown_raw,
            }],
        }
        print(raml.get("markdown"))
        assert dict_equal(raml, expected_data)


def test_invalid_yaml_tag():
    raml_file = os.path.join(EXAMPLES, "invalid_yaml_tag.raml")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(open(raml_file))

    msg = "Error parsing RAML:"
    assert msg in e.value.args[0]


def test_includes_has_invalid_tag():
    raml_file = os.path.join(EXAMPLES, "include_has_invalid_tag.raml")
    with pytest.raises(LoadRAMLError) as e:
        loader.RAMLLoader().load(open(raml_file))

    msg = "Error parsing RAML:"
    assert msg in e.value.args[0]


def test_json_ref_in_schema_relative_empty_fragment():
    raml_file = os.path.join(EXAMPLES, "json_include_with_ref_empty_fragment.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)
        expected_data = {
            "title": "Sample API Demo - JSON Includes",
            "version": "v1",
            "baseUri": "http://json.example.com",
            "schemas": [{
                "json": {
                    "name": "foo",
                    "second_name": "bar",
                    "false": True
                },
            }],
            "/foo": {
                "displayName": "foo resource"
            }
        }
        assert dict_equal(raml, expected_data)


def test_json_ref_in_schema_relative_nonempty_fragment():
    raml_file = os.path.join(EXAMPLES, "json_include_with_ref_nonempty_fragment.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)
        expected_data = {
            "title": "Sample API Demo - JSON Includes",
            "version": "v1",
            "baseUri": "http://json.example.com",
            "schemas": [{
                "json": {
                    "name": "foo",
                    "second_name": "bar"
                },
            }],
            "/foo": {
                "displayName": "foo resource"
            }
        }
        assert dict_equal(raml, expected_data)


def test_json_ref_in_schema_internal_fragment_reference():
    raml_file = os.path.join(EXAMPLES, "json_include_with_ref_internal_fragment.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)
        expected_data = {
            "title": "Sample API Demo - JSON Includes",
            "version": "v1",
            "baseUri": "http://json.example.com",
            "schemas": [{
                "json": {
                    "name": "foo",
                    "internal": "yes",
                },
            }],
            "/foo": {
                "displayName": "foo resource"
            }
        }
        assert dict_equal(raml, expected_data)


def test_json_ref_in_schema_absolute():
    # Set up the file with an absolute path
    with open(os.path.join(EXAMPLES, "includes",
                           "example_with_absolute_ref.json"), 'w') as f:
        f.write(json.dumps({
            "second_name": "bar",
            "$ref": "file://{0}#".format(
                os.path.join(EXAMPLES, "includes", "example.json")
            )
        }))

    # Now load it
    raml_file = os.path.join(EXAMPLES, "json_include_with_absolute_ref.raml")
    with open(raml_file) as f:
        raml = loader.RAMLLoader().load(f)
        expected_data = {
            "title": "Sample API Demo - JSON Includes",
            "version": "v1",
            "baseUri": "http://json.example.com",
            "schemas": [{
                "json": {
                    "name": "foo",
                    "second_name": "bar",
                    "false": True
                },
            }],
            "/foo": {
                "displayName": "foo resource"
            }
        }
        assert dict_equal(raml, expected_data)


def test_json_ref_in_schema_url():
    raml_file = os.path.join(EXAMPLES, "json_include_with_url_ref.raml")
    with open(raml_file) as r:
        raml = loader.RAMLLoader().load(r)
        expected_data = {
            "title": "Sample API Demo - JSON Includes",
            "version": "v1",
            "baseUri": "http://json.example.com",
            "schemas": [{
                "json": {
                    "name": "foo",
                    "second_name": "bar",
                    "false": True
                },
            }],
            "/foo": {
                "displayName": "foo resource"
            }
        }
        assert dict_equal(raml, expected_data)
