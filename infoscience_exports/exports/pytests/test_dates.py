from exports.marc21xml import set_year


def test_year_only():
    assert set_year('2018') == '2018'


def test_full_date():
    assert set_year('2018-01-01') == '2018'
    assert set_year('01-01-2018') == '2018'


def test_error():
    assert set_year('2018.01.01') == ''
