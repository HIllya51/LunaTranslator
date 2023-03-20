# This is a small test to make sure ipadic is usable
from fugashi import GenericTagger
import pytest
import ipadic

WAKATI_TESTS = (
        ("すももももももももの内", 'すもも も もも も もも の 内'),
        ("日本語ですよ", '日本語 です よ'),
        ("深海魚は、深海に生息する魚類の総称。", '深海魚 は 、 深海 に 生息 する 魚類 の 総称 。'),
        )

@pytest.mark.parametrize('text,wakati', WAKATI_TESTS)
def test_wakati(text, wakati):
    tagger = GenericTagger(ipadic.MECAB_ARGS + ' -Owakati')
    assert tagger.parse(text) == wakati
