#!/usr/bin/env pytest
import pytest
from icecream import ic

from door_commander.mqtt import unpack_topic

testdata = {
    ("", ""): [],
    ("#", ""): [[""]],
    ("+", ""): [""],
    ("#", "/"): [["", ""]],
    ("#", "foo"): [["foo"]],
    ("#", "foo/bar"): [["foo", "bar"]],
    ("foo/#", "foo/bar"): [["bar"]],
    ("foo/#", "foo/bar/baz"): [["bar", "baz"]],
    ("+/#", "foo/bar"): ["foo", ["bar"]],
    ("+/#", "foo/bar/baz"): ["foo", ["bar", "baz"]],
    ("foo/+/baz", "foo/bar/baz"): ["bar"],
    ("+/+/+", "foo/bar/baz"): ["foo", "bar", "baz"],
}

preprocessed_test_data = ((pattern, topic, matches) for (pattern, topic), matches in testdata.items())

invalid_testdata = [
    ("foo", ""),
    ("foo", "+"),
    ("foo", "#"),
    ("foo", ""),
    ("foo", "bar"),
    ("foo/+", "foo"),
    ("foo/+", "foo/bar/baz"),
    ("foo/#", "bar/foo"),
    ("foo/+", "bar/foo"),
    ("+/foo", "bar/baz"),
    ("#/foo", "bar/foo"),
]


@pytest.mark.parametrize("pattern, topic, matches", preprocessed_test_data)
def test_match(pattern, topic, matches):
    assert list(unpack_topic(pattern, topic)) == matches


@pytest.mark.parametrize("pattern, topic", invalid_testdata)
def test_fail(pattern, topic):
    with pytest.raises(Exception):
        list(unpack_topic(pattern, topic))

