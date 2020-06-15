from django.conf import settings

from exports.marc21xml import Author


def expected_url(name):
    return "{}/search?p={}".format("https://infoscience.epfl.ch", name)


def test_standard_case():
    author = Author("Emmanuel Bréton")
    assert author.fullname == "Emmanuel Bréton"
    assert author.search_url == expected_url("Emmanuel+Bréton")
    assert author.initname == "Emmanuel Bréton"


def test_search_url():
    assert Author("Jean-Marc Marco").search_url == expected_url("Jean-Marc+Marco")
    assert Author("Jean, Marc Marco").search_url == expected_url("Jean++Marc+Marco")


def test_initial_names():
    assert Author("Marco Jean Marc").initname == "Marco Jean Marc"
    assert Author("Marco, Jean").initname == "J. Marco"
    assert Author("Marco, Jean Marc").initname == "J. M. Marco"
    assert Author("Marco, Jean-Marc").initname == "J.-M. Marco"
