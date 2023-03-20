## NOTE: These tests are written again the 2.1.2 binary distribution of Unidic.

from fugashi import Tagger, UnidicFeatures17
import pytest

WAKATI_TESTS = (
        ("すももももももももの内", 'すもも も もも も もも の 内'),
        ("日本語ですよ", '日本 語 です よ'),
        ("深海魚は、深海に生息する魚類の総称。", '深海 魚 は 、 深海 に 生息 する 魚類 の 総称 。'),
        )

TOKENIZER_TESTS = (
        ('あなたは新米の魔女。', ['あなた', 'は', '新米', 'の', '魔女', '。']),
        ('パートナーである猫と共に、見知らぬ町へやってきたばかりです。', ['パートナー', 'で', 'ある', '猫', 'と', '共', 'に', '、', '見知ら', 'ぬ', '町', 'へ', 'やっ', 'て', 'き', 'た', 'ばかり', 'です', '。']),
        )

NBEST_TESTS = (
        ('外国人参政権', '外国 人参 政権 \n外国 人 参政 権'),
        ("深海魚は、深海に生息する魚類の総称。", '深海 魚 は 、 深海 に 生息 する 魚類 の 総称 。 \n深 海魚 は 、 深海 に 生息 する 魚類 の 総称 。'),
        ("東京都の大人気ない主材料", '東京 都 の 大 人気 ない 主材 料 \n東京 都 の 大 人気 ない 主 材料')
        )

POS_TESTS = (
        ('日本語', ['名詞,固有名詞,地名,国', '名詞,普通名詞,一般,*']),
        )

ACCENT_TESTS = (
        ('稻村に行きました', ['0,2', '*', '0', '*', '*']),
        )

@pytest.mark.parametrize('text,wakati', WAKATI_TESTS)
def test_wakati(text, wakati):
    tagger = Tagger('-Owakati')
    assert tagger.parse(text) == wakati

@pytest.mark.parametrize('text,saved', TOKENIZER_TESTS)
def test_tokens(text, saved):
    # testing the token objects is tricky, so instead just check surfaces
    #TODO: maybe save serialized nodes to compare?
    tagger = Tagger()
    tokens = [str(tok) for tok in tagger(text)]
    assert tokens == saved

@pytest.mark.parametrize('text,saved', NBEST_TESTS)
def test_nbest(text, saved):
    tagger = Tagger('-Owakati')
    assert tagger.nbest(text, 2) == saved

@pytest.mark.parametrize('text,saved', NBEST_TESTS)
def test_nbest_nodes(text, saved):
    tagger = Tagger()
    # parse adds a space to the end of each line
    saved = [ss.strip() for ss in saved.split("\n")]
    res = tagger.nbestToNodeList(text, 2)
    out = [" ".join([nn.surface for nn in nodes]) for nodes in res]
    assert out == saved

def test_invalid_args():
    # Invalid args will give a NULL pointer for the Tagger object
    # don't try to use the null object!
    with pytest.raises(RuntimeError):
        tagger = Tagger('-fail')

@pytest.mark.parametrize('text,tags', POS_TESTS)
def test_pos(text, tags):
    # There should be a pos property when using the default tagger
    tagger = Tagger()
    tags_ = [tok.pos for tok in tagger(text)]
    assert tags == tags_

@pytest.mark.parametrize('text,accent', ACCENT_TESTS)
def test_accent(text, accent):
    # This checks for correct handling of feature fields containing commas as reported in #13
    tagger = Tagger()
    tokens = tagger(text)
    # Skip if UnidicFeatures17 is used because it doesn't have 'atype' attribute
    if tokens and isinstance(tokens[0].feature, UnidicFeatures17):
        pytest.skip()
    accent_ = [tok.feature.aType for tok in tokens]
    assert accent_ == accent

def test_clobber():
    # Check that memory isn't clobbered by repeated parse calls
    tagger = Tagger()
    nodes1 = tagger("a b c d")
    nodes2 = tagger("x y z !")

    assert "a b c d".split() == [nn.surface for nn in nodes1]
