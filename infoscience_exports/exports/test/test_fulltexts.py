from exports.marc21xml import set_fulltext


def test_no_fulltext():
    assert set_fulltext([]) == ''


def test_no_pdfs():
    assert set_fulltext(["http://infoscience.epfl.ch/record/253539/files/Poster.ppt"]) == ''
    assert set_fulltext(["https://www.frontiersin.org/articles/10.3389/fnbot.2017.00057/full"]) == ''


def test_only_one_pdf():
    # one pdf
    assert set_fulltext(["http://infoscience.epfl.ch/record/253637/files/write%20nanoscale.pdf"]) \
        == 'http://infoscience.epfl.ch/record/253637/files/write%20nanoscale.pdf'

    # one pdfa
    assert set_fulltext(["http://infoscience.epfl.ch/record/253144/files/2018_ICIT_Coulinge.pdf?subformat=pdfa"]) \
        == "http://infoscience.epfl.ch/record/253144/files/2018_ICIT_Coulinge.pdf"

    # one pdf & one asp
    assert set_fulltext([
        "https://ibeton.epfl.ch/util/script/sendArticle.asp?R=Cantone16",
        "http://infoscience.epfl.ch/record/82377/files/JEP96-3.pdf"]) \
        == 'http://infoscience.epfl.ch/record/82377/files/JEP96-3.pdf'

    # one pdf in 2 formats
    assert set_fulltext([
        "http://infoscience.epfl.ch/record/253610/files/paper.pdf",
        "http://infoscience.epfl.ch/record/253610/files/paper.pdf?subformat=pdfa"]) \
        == 'http://infoscience.epfl.ch/record/253610/files/paper.pdf'


def test_only_mutiple_pdfs():
    # two pdfs
    assert set_fulltext([
        "http://publications.idiap.ch/downloads/reports/1996/JEP96-3.pdf",
        "http://infoscience.epfl.ch/record/82377/files/JEP96-3.pdf"]) \
        == 'http://infoscience.epfl.ch/record/82377/files'

    # two pdfs along with their pdfas
    assert set_fulltext([
        "http://infoscience.epfl.ch/record/253610/files/paper.pdf",
        "http://infoscience.epfl.ch/record/253610/files/paper.pdf?subformat=pdfa",
        "http://infoscience.epfl.ch/record/253610/files/supplemental.pdf",
        "http://infoscience.epfl.ch/record/253610/files/supplemental.pdf?subformat=pdfa"]) \
        == 'http://infoscience.epfl.ch/record/253610/files'

    # mix
    assert set_fulltext([
        "https://ibeton.epfl.ch/util/script/sendArticle.asp?R=Cantone16",
        "http://infoscience.epfl.ch/record/253610/files/paper.pdf",
        "http://infoscience.epfl.ch/record/253610/files/supplemental.pdf",
        "http://infoscience.epfl.ch/record/253610/files/supplemental.pdf?subformat=pdfa"]) \
        == 'http://infoscience.epfl.ch/record/253610/files'
