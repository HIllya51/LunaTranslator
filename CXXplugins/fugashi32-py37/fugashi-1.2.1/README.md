[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/polm/fugashi-streamlit-demo/main/demo.py)
[![Current PyPI packages](https://badge.fury.io/py/fugashi.svg)](https://pypi.org/project/fugashi/)
![Test Status](https://github.com/polm/fugashi/workflows/test-manylinux/badge.svg)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/fugashi)](https://pypi.org/project/fugashi/)
![Supported Platforms](https://img.shields.io/badge/platforms-linux%20macosx%20windows-blue)

# fugashi

<img src="https://github.com/polm/fugashi/raw/master/fugashi.png" width=125 height=125 alt="fugashi by Irasutoya" />

fugashi is a Cython wrapper for [MeCab](https://taku910.github.io/mecab/), a
Japanese tokenizer and morphological analysis tool.  Wheels are provided for
Linux, OSX, and Win64, and UniDic is [easy to install](#installing-a-dictionary).

**issueを英語で書く必要はありません。**

Check out the [interactive demo][], see the [blog post](https://www.dampfkraft.com/nlp/fugashi.html) for background
on why fugashi exists and some of the design decisions, or see [this
guide][guide] for a basic introduction to Japanese tokenization.

[guide]: https://www.dampfkraft.com/nlp/how-to-tokenize-japanese.html
[interactive demo]: https://share.streamlit.io/polm/fugashi-streamlit-demo/main/demo.py

If you are on an unsupported platform (like PowerPC), you'll need to install
MeCab first. It's recommended you install [from
source](https://github.com/taku910/mecab). If you need to build from source on
Windows, [@chezou's fork](https://github.com/chezou/mecab) is recommended; see
[issue #44](https://github.com/polm/fugashi/issues/44#issuecomment-954426115)
for an explanation of the problems with the official repo.

## Usage

```python
from fugashi import Tagger

tagger = Tagger('-Owakati')
text = "麩菓子は、麩を主材料とした日本の菓子。"
tagger.parse(text)
# => '麩 菓子 は 、 麩 を 主材 料 と し た 日本 の 菓子 。'
for word in tagger(text):
    print(word, word.feature.lemma, word.pos, sep='\t')
    # "feature" is the Unidic feature data as a named tuple
```

## Installing a Dictionary

fugashi requires a dictionary. [UniDic](https://unidic.ninjal.ac.jp/) is
recommended, and two easy-to-install versions are provided.

  - [unidic-lite](https://github.com/polm/unidic-lite), a slightly modified version 2.1.2 of Unidic (from 2013) that's relatively small
  - [unidic](https://github.com/polm/unidic-py), the latest UniDic 3.1.0, which is 770MB on disk and requires a separate download step

If you just want to make sure things work you can start with `unidic-lite`, but
for more serious processing `unidic` is recommended. For production use you'll
generally want to generate your own dictionary too; for details see the [MeCab
documentation](https://taku910.github.io/mecab/learn.html).

To get either of these dictionaries, you can install them directly using `pip`
or do the below:

```sh
pip install fugashi[unidic-lite]

# The full version of UniDic requires a separate download step
pip install fugashi[unidic]
python -m unidic download
```

For more information on the different MeCab dictionaries available, see [this article](https://www.dampfkraft.com/nlp/japanese-tokenizer-dictionaries.html).

## Dictionary Use

fugashi is written with the assumption you'll use Unidic to process Japanese,
but it supports arbitrary dictionaries. 

If you're using a dictionary besides Unidic you can use the GenericTagger like this:

```python
from fugashi import GenericTagger
tagger = GenericTagger()

# parse can be used as normal
tagger.parse('something')
# features from the dictionary can be accessed by field numbers
for word in tagger(text):
    print(word.surface, word.feature[0])
```

You can also create a dictionary wrapper to get feature information as a named tuple. 

```python
from fugashi import GenericTagger, create_feature_wrapper
CustomFeatures = create_feature_wrapper('CustomFeatures', 'alpha beta gamma')
tagger = GenericTagger(wrapper=CustomFeatures)
for word in tagger.parseToNodeList(text):
    print(word.surface, word.feature.alpha)
```

## Citation

If you use fugashi in research, it would be appreciated if you cite this paper. You can read it at [the ACL Anthology](https://www.aclweb.org/anthology/2020.nlposs-1.7/) or [on Arxiv](https://arxiv.org/abs/2010.06858).

    @inproceedings{mccann-2020-fugashi,
        title = "fugashi, a Tool for Tokenizing {J}apanese in Python",
        author = "McCann, Paul",
        booktitle = "Proceedings of Second Workshop for NLP Open Source Software (NLP-OSS)",
        month = nov,
        year = "2020",
        address = "Online",
        publisher = "Association for Computational Linguistics",
        url = "https://www.aclweb.org/anthology/2020.nlposs-1.7",
        pages = "44--51",
        abstract = "Recent years have seen an increase in the number of large-scale multilingual NLP projects. However, even in such projects, languages with special processing requirements are often excluded. One such language is Japanese. Japanese is written without spaces, tokenization is non-trivial, and while high quality open source tokenizers exist they can be hard to use and lack English documentation. This paper introduces fugashi, a MeCab wrapper for Python, and gives an introduction to tokenizing Japanese.",
    }

## Alternatives

If you have a problem with fugashi feel free to open an issue. However, there
are some cases where it might be better to use a different library.

- If you don't want to deal with installing MeCab at all, try [SudachiPy](https://github.com/WorksApplications/sudachi.rs).
- If you need to work with Korean, try [pymecab-ko](https://github.com/NoUnique/pymecab-ko) or [KoNLPy](https://konlpy.org/en/latest/).

## License and Copyright Notice

fugashi is released under the terms of the [MIT license](./LICENSE). Please
copy it far and wide.

fugashi is a wrapper for MeCab, and fugashi wheels include MeCab binaries.
MeCab is copyrighted free software by Taku Kudo `<taku@chasen.org>` and Nippon
Telegraph and Telephone Corporation, and is redistributed under the [BSD
License](./LICENSE.mecab).
