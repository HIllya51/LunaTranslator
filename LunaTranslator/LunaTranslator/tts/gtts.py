# -*- coding: utf-8 -*-
import base64
import json, time
import logging, os
import re
import urllib
from myutils.proxy import getproxy
import requests

_langs = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fi": "Finnish",
    "fr": "French",
    "gu": "Gujarati",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "iw": "Hebrew",
    "ja": "Japanese",
    "jw": "Javanese",
    "km": "Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "la": "Latin",
    "lv": "Latvian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ms": "Malay",
    "my": "Myanmar (Burmese)",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "si": "Sinhala",
    "sk": "Slovak",
    "sq": "Albanian",
    "sr": "Serbian",
    "su": "Sundanese",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Filipino",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
}


def _main_langs():
    return _langs


from warnings import warn
import logging

__all__ = ["tts_langs"]

# Logger
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def tts_langs():
    """Languages Google Text-to-Speech supports.

    Returns:
        dict: A dictionary of the type `{ '<lang>': '<name>'}`

            Where `<lang>` is an IETF language tag such as `en` or `zh-TW`,
            and `<name>` is the full English name of the language, such as
            `English` or `Chinese (Mandarin/Taiwan)`.

    The dictionary returned combines languages from two origins:

    - Languages fetched from Google Translate (pre-generated in :mod:`gtts.langs`)
    - Languages that are undocumented variations that were observed to work and
      present different dialects or accents.

    """
    langs = dict()
    langs.update(_main_langs())
    langs.update(_extra_langs())
    log.debug("langs: {}".format(langs))
    return langs


def _extra_langs():
    """Define extra languages.

    Returns:
        dict: A dictionary of extra languages manually defined.

            Variations of the ones generated in `_main_langs`,
            observed to provide different dialects or accents or
            just simply accepted by the Google Translate Text-to-Speech API.

    """
    return {
        # Chinese
        "zh-TW": "Chinese (Mandarin/Taiwan)",
        "zh": "Chinese (Mandarin)",
    }


def _fallback_deprecated_lang(lang):
    """Languages Google Text-to-Speech used to support.

    Language tags that don't work anymore, but that can
    fallback to a more general language code to maintain
    compatibility.

    Args:
        lang (string): The language tag.

    Returns:
        string: The language tag, as-is if not deprecated,
            or a fallback if it exits.

    Example:
        ``en-GB`` returns ``en``.
        ``en-gb`` returns ``en``.

    """

    deprecated = {
        # '<fallback>': [<list of deprecated langs>]
        "en": [
            "en-us",
            "en-ca",
            "en-uk",
            "en-gb",
            "en-au",
            "en-gh",
            "en-in",
            "en-ie",
            "en-nz",
            "en-ng",
            "en-ph",
            "en-za",
            "en-tz",
        ],
        "fr": ["fr-ca", "fr-fr"],
        "pt": ["pt-br", "pt-pt"],
        "es": ["es-es", "es-us"],
        "zh-CN": ["zh-cn"],
        "zh-TW": ["zh-tw"],
    }

    for fallback_lang, deprecated_langs in deprecated.items():
        if lang.lower() in deprecated_langs:
            msg = (
                "'{}' has been deprecated, falling back to '{}'. "
                "This fallback will be removed in a future version."
            ).format(lang, fallback_lang)

            warn(msg, DeprecationWarning)
            log.warning(msg)

            return fallback_lang

    return lang


# -*- coding: utf-8 -*-
import re


class symbols:
    # -*- coding: utf-8 -*-

    ABBREVIATIONS = ["dr", "jr", "mr", "mrs", "ms", "msgr", "prof", "sr", "st"]

    SUB_PAIRS = [("Esq.", "Esquire")]

    ALL_PUNC = "?!？！.,¡()[]¿…‥،;:—。，、：\n"

    TONE_MARKS = "?!？！"

    PERIOD_COMMA = ".,"

    COLON = ":"


class RegexBuilder:
    r"""Builds regex using arguments passed into a pattern template.

    Builds a regex object for which the pattern is made from an argument
    passed into a template. If more than one argument is passed (iterable),
    each pattern is joined by "|" (regex alternation 'or') to create a
    single pattern.

    Args:
        pattern_args (iteratable): String element(s) to be each passed to
            ``pattern_func`` to create a regex pattern. Each element is
            ``re.escape``'d before being passed.
        pattern_func (callable): A 'template' function that should take a
            string and return a string. It should take an element of
            ``pattern_args`` and return a valid regex pattern group string.
        flags: ``re`` flag(s) to compile with the regex.

    Example:
        To create a simple regex that matches on the characters "a", "b",
        or "c", followed by a period::

            >>> rb = RegexBuilder('abc', lambda x: "{}\.".format(x))

        Looking at ``rb.regex`` we get the following compiled regex::

            >>> print(rb.regex)
            'a\.|b\.|c\.'

        The above is fairly simple, but this class can help in writing more
        complex repetitive regex, making them more readable and easier to
        create by using existing data structures.

    Example:
        To match the character following the words "lorem", "ipsum", "meili"
        or "koda"::

            >>> words = ['lorem', 'ipsum', 'meili', 'koda']
            >>> rb = RegexBuilder(words, lambda x: "(?<={}).".format(x))

        Looking at ``rb.regex`` we get the following compiled regex::

            >>> print(rb.regex)
            '(?<=lorem).|(?<=ipsum).|(?<=meili).|(?<=koda).'

    """

    def __init__(self, pattern_args, pattern_func, flags=0):
        self.pattern_args = pattern_args
        self.pattern_func = pattern_func
        self.flags = flags

        # Compile
        self.regex = self._compile()

    def _compile(self):
        alts = []
        for arg in self.pattern_args:
            arg = re.escape(arg)
            alt = self.pattern_func(arg)
            alts.append(alt)

        pattern = "|".join(alts)
        return re.compile(pattern, self.flags)

    def __repr__(self):  # pragma: no cover
        return str(self.regex)


class PreProcessorRegex:
    r"""Regex-based substitution text pre-processor.

    Runs a series of regex substitutions (``re.sub``) from each ``regex`` of a
    :class:`gtts.tokenizer.core.RegexBuilder` with an extra ``repl``
    replacement parameter.

    Args:
        search_args (iteratable): String element(s) to be each passed to
            ``search_func`` to create a regex pattern. Each element is
            ``re.escape``'d before being passed.
        search_func (callable): A 'template' function that should take a
            string and return a string. It should take an element of
            ``search_args`` and return a valid regex search pattern string.
        repl (string): The common replacement passed to the ``sub`` method for
            each ``regex``. Can be a raw string (the case of a regex
            backreference, for example)
        flags: ``re`` flag(s) to compile with each `regex`.

    Example:
        Add "!" after the words "lorem" or "ipsum", while ignoring case::

            >>> import re
            >>> words = ['lorem', 'ipsum']
            >>> pp = PreProcessorRegex(words,
            ...                        lambda x: "({})".format(x), r'\\1!',
            ...                        re.IGNORECASE)

        In this case, the regex is a group and the replacement uses its
        backreference ``\\1`` (as a raw string). Looking at ``pp`` we get the
        following list of search/replacement pairs::

            >>> print(pp)
            (re.compile('(lorem)', re.IGNORECASE), repl='\1!'),
            (re.compile('(ipsum)', re.IGNORECASE), repl='\1!')

        It can then be run on any string of text::

            >>> pp.run("LOREM ipSuM")
            "LOREM! ipSuM!"

    See :mod:`gtts.tokenizer.pre_processors` for more examples.

    """

    def __init__(self, search_args, search_func, repl, flags=0):
        self.repl = repl

        # Create regex list
        self.regexes = []
        for arg in search_args:
            rb = RegexBuilder([arg], search_func, flags)
            self.regexes.append(rb.regex)

    def run(self, text):
        """Run each regex substitution on ``text``.

        Args:
            text (string): the input text.

        Returns:
            string: text after all substitutions have been sequentially
            applied.

        """
        for regex in self.regexes:
            text = regex.sub(self.repl, text)
        return text

    def __repr__(self):  # pragma: no cover
        subs_strs = []
        for r in self.regexes:
            subs_strs.append("({}, repl='{}')".format(r, self.repl))
        return ", ".join(subs_strs)


class PreProcessorSub:
    r"""Simple substitution text preprocessor.

    Performs string-for-string substitution from list a find/replace pairs.
    It abstracts :class:`gtts.tokenizer.core.PreProcessorRegex` with a default
    simple substitution regex.

    Args:
        sub_pairs (list): A list of tuples of the style
            ``(<search str>, <replace str>)``
        ignore_case (bool): Ignore case during search. Defaults to ``True``.

    Example:
        Replace all occurences of "Mac" to "PC" and "Firefox" to "Chrome"::

            >>> sub_pairs = [('Mac', 'PC'), ('Firefox', 'Chrome')]
            >>> pp = PreProcessorSub(sub_pairs)

        Looking at the ``pp``, we get the following list of
        search (regex)/replacement pairs::

            >>> print(pp)
            (re.compile('Mac', re.IGNORECASE), repl='PC'),
            (re.compile('Firefox', re.IGNORECASE), repl='Chrome')

        It can then be run on any string of text::

            >>> pp.run("I use firefox on my mac")
            "I use Chrome on my PC"

    See :mod:`gtts.tokenizer.pre_processors` for more examples.

    """

    def __init__(self, sub_pairs, ignore_case=True):
        def search_func(x):
            return "{}".format(x)

        flags = re.I if ignore_case else 0

        # Create pre-processor list
        self.pre_processors = []
        for sub_pair in sub_pairs:
            pattern, repl = sub_pair
            pp = PreProcessorRegex([pattern], search_func, repl, flags)
            self.pre_processors.append(pp)

    def run(self, text):
        """Run each substitution on ``text``.

        Args:
            text (string): the input text.

        Returns:
            string: text after all substitutions have been sequentially
            applied.

        """
        for pp in self.pre_processors:
            text = pp.run(text)
        return text

    def __repr__(self):  # pragma: no cover
        return ", ".join([str(pp) for pp in self.pre_processors])


class Tokenizer:
    r"""An extensible but simple generic rule-based tokenizer.

    A generic and simple string tokenizer that takes a list of functions
    (called `tokenizer cases`) returning ``regex`` objects and joins them by
    "|" (regex alternation 'or') to create a single regex to use with the
    standard ``regex.split()`` function.

    ``regex_funcs`` is a list of any function that can return a ``regex``
    (from ``re.compile()``) object, such as a
    :class:`gtts.tokenizer.core.RegexBuilder` instance (and its ``regex``
    attribute).

    See the :mod:`gtts.tokenizer.tokenizer_cases` module for examples.

    Args:
        regex_funcs (list): List of compiled ``regex`` objects. Each
            function's pattern will be joined into a single pattern and
            compiled.
        flags: ``re`` flag(s) to compile with the final regex. Defaults to
            ``re.IGNORECASE``

    Note:
        When the ``regex`` objects obtained from ``regex_funcs`` are joined,
        their individual ``re`` flags are ignored in favour of ``flags``.

    Raises:
        TypeError: When an element of ``regex_funcs`` is not a function, or
            a function that does not return a compiled ``regex`` object.

    Warning:
        Joined ``regex`` patterns can easily interfere with one another in
        unexpected ways. It is recommanded that each tokenizer case operate
        on distinct or non-overlapping chracters/sets of characters
        (For example, a tokenizer case for the period (".") should also
        handle not matching/cutting on decimals, instead of making that
        a seperate tokenizer case).

    Example:
        A tokenizer with a two simple case (*Note: these are bad cases to
        tokenize on, this is simply a usage example*)::

            >>> import re, RegexBuilder
            >>>
            >>> def case1():
            ...     return re.compile("\,")
            >>>
            >>> def case2():
            ...     return RegexBuilder('abc', lambda x: "{}\.".format(x)).regex
            >>>
            >>> t = Tokenizer([case1, case2])

        Looking at ``case1().pattern``, we get::

            >>> print(case1().pattern)
            '\\,'

        Looking at ``case2().pattern``, we get::

            >>> print(case2().pattern)
            'a\\.|b\\.|c\\.'

        Finally, looking at ``t``, we get them combined::

            >>> print(t)
            're.compile('\\,|a\\.|b\\.|c\\.', re.IGNORECASE)
             from: [<function case1 at 0x10bbcdd08>, <function case2 at 0x10b5c5e18>]'

        It can then be run on any string of text::

            >>> t.run("Hello, my name is Linda a. Call me Lin, b. I'm your friend")
            ['Hello', ' my name is Linda ', ' Call me Lin', ' ', " I'm your friend"]

    """

    def __init__(self, regex_funcs, flags=re.IGNORECASE):
        self.regex_funcs = regex_funcs
        self.flags = flags

        try:
            # Combine
            self.total_regex = self._combine_regex()
        except (TypeError, AttributeError) as e:  # pragma: no cover
            raise TypeError(
                "Tokenizer() expects a list of functions returning "
                "regular expression objects (i.e. re.compile). " + str(e)
            )

    def _combine_regex(self):
        alts = []
        for func in self.regex_funcs:
            alts.append(func())

        pattern = "|".join(alt.pattern for alt in alts)
        return re.compile(pattern, self.flags)

    def run(self, text):
        """Tokenize `text`.

        Args:
            text (string): the input text to tokenize.

        Returns:
            list: A list of strings (token) split according to the tokenizer cases.

        """
        return self.total_regex.split(text)

    def __repr__(self):  # pragma: no cover
        return str(self.total_regex) + " from: " + str(self.regex_funcs)


class tokenizer_cases:

    def tone_marks():
        """Keep tone-modifying punctuation by matching following character.

        Assumes the `tone_marks` pre-processor was run for cases where there might
        not be any space after a tone-modifying punctuation mark.
        """
        return RegexBuilder(
            pattern_args=symbols.TONE_MARKS, pattern_func=lambda x: "(?<={}).".format(x)
        ).regex

    def period_comma():
        """Period and comma case.

        Match if not preceded by ".<letter>" and only if followed by space.
        Won't cut in the middle/after dotted abbreviations; won't cut numbers.

        Note:
            Won't match if a dotted abbreviation ends a sentence.

        Note:
            Won't match the end of a sentence if not followed by a space.

        """
        return RegexBuilder(
            pattern_args=symbols.PERIOD_COMMA,
            pattern_func=lambda x: r"(?<!\.[a-z]){} ".format(x),
        ).regex

    def colon():
        """Colon case.

        Match a colon ":" only if not preceded by a digit.
        Mainly to prevent a cut in the middle of time notations e.g. 10:01

        """
        return RegexBuilder(
            pattern_args=symbols.COLON, pattern_func=lambda x: r"(?<!\d){}".format(x)
        ).regex

    def other_punctuation():
        """Match other punctuation.

        Match other punctuation to split on; punctuation that naturally
        inserts a break in speech.

        """
        punc = "".join(
            set(symbols.ALL_PUNC)
            - set(symbols.TONE_MARKS)
            - set(symbols.PERIOD_COMMA)
            - set(symbols.COLON)
        )
        return RegexBuilder(
            pattern_args=punc, pattern_func=lambda x: "{}".format(x)
        ).regex

    def legacy_all_punctuation():  # pragma: no cover b/c tested but Coveralls: ¯\_(ツ)_/¯
        """Match all punctuation.

        Use as only tokenizer case to mimic gTTS 1.x tokenization.
        """
        punc = symbols.ALL_PUNC
        return RegexBuilder(
            pattern_args=punc, pattern_func=lambda x: "{}".format(x)
        ).regex


class pre_processors:

    def tone_marks(text):
        """Add a space after tone-modifying punctuation.

        Because the `tone_marks` tokenizer case will split after a tone-modifying
        punctuation mark, make sure there's whitespace after.

        """
        return PreProcessorRegex(
            search_args=symbols.TONE_MARKS,
            search_func=lambda x: "(?<={})".format(x),
            repl=" ",
        ).run(text)

    def end_of_line(text):
        """Re-form words cut by end-of-line hyphens.

        Remove "<hyphen><newline>".

        """
        return PreProcessorRegex(
            search_args="-", search_func=lambda x: "{}\n".format(x), repl=""
        ).run(text)

    def abbreviations(text):
        """Remove periods after an abbreviation from a list of known
        abbreviations that can be spoken the same without that period. This
        prevents having to handle tokenization of that period.

        Note:
            Could potentially remove the ending period of a sentence.

        Note:
            Abbreviations that Google Translate can't pronounce without
            (or even with) a period should be added as a word substitution with a
            :class:`PreProcessorSub` pre-processor. Ex.: 'Esq.', 'Esquire'.

        """
        return PreProcessorRegex(
            search_args=symbols.ABBREVIATIONS,
            search_func=lambda x: r"(?<={})(?=\.).".format(x),
            repl="",
            flags=re.IGNORECASE,
        ).run(text)

    def word_sub(text):
        """Word-for-word substitutions."""
        return PreProcessorSub(sub_pairs=symbols.SUB_PAIRS).run(text)


punc = symbols.ALL_PUNC
from string import whitespace as ws
import re

_ALL_PUNC_OR_SPACE = re.compile("^[{}]*$".format(re.escape(punc + ws)))
"""Regex that matches if an entire line is only comprised
of whitespace and punctuation

"""


def _minimize(the_string, delim, max_size):
    """Recursively split a string in the largest chunks
    possible from the highest position of a delimiter all the way
    to a maximum size

    Args:
        the_string (string): The string to split.
        delim (string): The delimiter to split on.
        max_size (int): The maximum size of a chunk.

    Returns:
        list: the minimized string in tokens

    Every chunk size will be at minimum ``the_string[0:idx]`` where ``idx``
    is the highest index of ``delim`` found in ``the_string``; and at maximum
    ``the_string[0:max_size]`` if no ``delim`` was found in ``the_string``.
    In the latter case, the split will occur at ``the_string[max_size]``
    which can be any character. The function runs itself again on the rest of
    ``the_string`` (``the_string[idx:]``) until no chunk is larger than
    ``max_size``.

    """
    # Remove `delim` from start of `the_string`
    # i.e. prevent a recursive infinite loop on `the_string[0:0]`
    # if `the_string` starts with `delim` and is larger than `max_size`
    if the_string.startswith(delim):
        the_string = the_string[len(delim) :]

    if len(the_string) > max_size:
        try:
            # Find the highest index of `delim` in `the_string[0:max_size]`
            # i.e. `the_string` will be cut in half on `delim` index
            idx = the_string.rindex(delim, 0, max_size)
        except ValueError:
            # `delim` not found in `the_string`, index becomes `max_size`
            # i.e. `the_string` will be cut in half arbitrarily on `max_size`
            idx = max_size
        # Call itself again for `the_string[idx:]`
        return [the_string[:idx]] + _minimize(the_string[idx:], delim, max_size)
    else:
        return [the_string]


def _clean_tokens(tokens):
    """Clean a list of strings

    Args:
        tokens (list): A list of strings (tokens) to clean.

    Returns:
        list: Stripped strings ``tokens`` without the original elements
            that only consisted of whitespace and/or punctuation characters.

    """
    return [t.strip() for t in tokens if not _ALL_PUNC_OR_SPACE.match(t)]


def _translate_url(tld="com", path=""):
    """Generates a Google Translate URL

    Args:
        tld (string): Top-level domain for the Google Translate host,
            i.e ``https://translate.google.<tld>``. Default is ``com``.
        path: (string): A path to append to the Google Translate host,
            i.e ``https://translate.google.com/<path>``. Default is ``""``.

    Returns:
        string: A Google Translate URL `https://translate.google.<tld>/path`
    """
    _GOOGLE_TTS_URL = "https://translate.google.{}/{}"
    return _GOOGLE_TTS_URL.format(tld, path)


__all__ = ["gTTS", "gTTSError"]

# Logger
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Speed:
    """Read Speed

    The Google TTS Translate API supports two speeds:
        Slow: True
        Normal: None
    """

    SLOW = True
    NORMAL = None


class gTTS:
    """gTTS -- Google Text-to-Speech.

    An interface to Google Translate's Text-to-Speech API.

    Args:
        text (string): The text to be read.
        tld (string): Top-level domain for the Google Translate host,
            i.e `https://translate.google.<tld>`. Different Google domains
            can produce different localized 'accents' for a given
            language. This is also useful when ``google.com`` might be blocked
            within a network but a local or different Google host
            (e.g. ``google.com.hk``) is not. Default is ``com``.
        lang (string, optional): The language (IETF language tag) to
            read the text in. Default is ``en``.
        slow (bool, optional): Reads text more slowly. Defaults to ``False``.
        lang_check (bool, optional): Strictly enforce an existing ``lang``,
            to catch a language error early. If set to ``True``,
            a ``ValueError`` is raised if ``lang`` doesn't exist.
            Setting ``lang_check`` to ``False`` skips Web requests
            (to validate language) and therefore speeds up instantiation.
            Default is ``True``.
        pre_processor_funcs (list): A list of zero or more functions that are
            called to transform (pre-process) text before tokenizing. Those
            functions must take a string and return a string. Defaults to::

                [
                    pre_processors.tone_marks,
                    pre_processors.end_of_line,
                    pre_processors.abbreviations,
                    pre_processors.word_sub
                ]

        tokenizer_func (callable): A function that takes in a string and
            returns a list of string (tokens). Defaults to::

                Tokenizer([
                    tokenizer_cases.tone_marks,
                    tokenizer_cases.period_comma,
                    tokenizer_cases.colon,
                    tokenizer_cases.other_punctuation
                ]).run

        timeout (float or tuple, optional): Seconds to wait for the server to
            send data before giving up, as a float, or a ``(connect timeout,
            read timeout)`` tuple. ``None`` will wait forever (default).

    See Also:
        :doc:`Pre-processing and tokenizing <tokenizer>`

    Raises:
        AssertionError: When ``text`` is ``None`` or empty; when there's nothing
            left to speak after pre-precessing, tokenizing and cleaning.
        ValueError: When ``lang_check`` is ``True`` and ``lang`` is not supported.
        RuntimeError: When ``lang_check`` is ``True`` but there's an error loading
            the languages dictionary.

    """

    GOOGLE_TTS_MAX_CHARS = 100  # Max characters the Google TTS API takes at a time
    GOOGLE_TTS_HEADERS = {
        "Referer": "http://translate.google.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/47.0.2526.106 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    GOOGLE_TTS_RPC = "jQ1olc"

    def __init__(
        self,
        text,
        tld="com",
        lang="en",
        slow=False,
        lang_check=True,
        pre_processor_funcs=[
            pre_processors.tone_marks,
            pre_processors.end_of_line,
            pre_processors.abbreviations,
            pre_processors.word_sub,
        ],
        tokenizer_func=Tokenizer(
            [
                tokenizer_cases.tone_marks,
                tokenizer_cases.period_comma,
                tokenizer_cases.colon,
                tokenizer_cases.other_punctuation,
            ]
        ).run,
        timeout=None,
    ):

        # Debug
        for k, v in dict(locals()).items():
            if k == "self":
                continue
            log.debug("%s: %s", k, v)

        # Text
        assert text, "No text to speak"
        self.text = text

        # Translate URL top-level domain
        self.tld = tld

        # Language
        self.lang_check = lang_check
        self.lang = lang

        if self.lang_check:
            # Fallback lang in case it is deprecated
            self.lang = _fallback_deprecated_lang(lang)

            try:
                langs = tts_langs()
                if self.lang not in langs:
                    raise ValueError("Language not supported: %s" % lang)
            except RuntimeError as e:
                log.debug(str(e), exc_info=True)
                log.warning(str(e))

        # Read speed
        if slow:
            self.speed = Speed.SLOW
        else:
            self.speed = Speed.NORMAL

        # Pre-processors and tokenizer
        self.pre_processor_funcs = pre_processor_funcs
        self.tokenizer_func = tokenizer_func

        self.timeout = timeout

    def _tokenize(self, text):
        # Pre-clean
        text = text.strip()

        # Apply pre-processors
        for pp in self.pre_processor_funcs:
            log.debug("pre-processing: %s", pp)
            text = pp(text)

        if len(text) <= self.GOOGLE_TTS_MAX_CHARS:
            return _clean_tokens([text])

        # Tokenize
        log.debug("tokenizing: %s", self.tokenizer_func)
        tokens = self.tokenizer_func(text)

        # Clean
        tokens = _clean_tokens(tokens)

        # Minimize
        min_tokens = []
        for t in tokens:
            min_tokens += _minimize(t, " ", self.GOOGLE_TTS_MAX_CHARS)

        # Filter empty tokens, post-minimize
        tokens = [t for t in min_tokens if t]

        return tokens

    def _prepare_requests(self):
        """Created the TTS API the request(s) without sending them.

        Returns:
            list: ``requests.PreparedRequests_``. <https://2.python-requests.org/en/master/api/#requests.PreparedRequest>`_``.
        """
        # TTS API URL
        translate_url = _translate_url(
            tld=self.tld, path="_/TranslateWebserverUi/data/batchexecute"
        )

        text_parts = self._tokenize(self.text)
        log.debug("text_parts: %s", str(text_parts))
        log.debug("text_parts: %i", len(text_parts))
        assert text_parts, "No text to send to TTS API"

        prepared_requests = []
        for idx, part in enumerate(text_parts):
            data = self._package_rpc(part)

            log.debug("data-%i: %s", idx, data)

            # Request
            r = requests.post(
                url=translate_url,
                data=data,
                headers=self.GOOGLE_TTS_HEADERS,
                proxies=getproxy(),
            )

            # Prepare request
            prepared_requests.append(r)

        return prepared_requests

    def _package_rpc(self, text):
        parameter = [text, self.lang, self.speed, "null"]
        escaped_parameter = json.dumps(parameter, separators=(",", ":"))

        rpc = [[[self.GOOGLE_TTS_RPC, escaped_parameter, None, "generic"]]]
        espaced_rpc = json.dumps(rpc, separators=(",", ":"))
        return "f.req={}&".format(urllib.parse.quote(espaced_rpc))

    def stream(self):
        """Do the TTS API request(s) and stream bytes

        Raises:
            :class:`gTTSError`: When there's an error with the API request.

        """
        # When disabling ssl verify in requests (for proxies and firewalls),
        # urllib3 prints an insecure warning on stdout. We disable that.
        try:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
            )
        except:
            pass

        prepared_requests = self._prepare_requests()
        for idx, r in enumerate(prepared_requests):

            # Write
            for line in r.content.split(b"\n"):
                decoded_line = line.decode("utf-8")
                if "jQ1olc" in decoded_line:
                    audio_search = re.search(r'jQ1olc","\[\\"(.*)\\"]', decoded_line)
                    if audio_search:
                        as_bytes = audio_search.group(1).encode("ascii")
                        yield base64.b64decode(as_bytes)
                    else:
                        # Request successful, good response,
                        # no audio stream in response
                        raise gTTSError(tts=self, response=r)
            log.debug("part-%i created", idx)

    def write_to_fp(self, fp):
        """Do the TTS API request(s) and write bytes to a file-like object.

        Args:
            fp (file object): Any file-like object to write the ``mp3`` to.

        Raises:
            :class:`gTTSError`: When there's an error with the API request.
            TypeError: When ``fp`` is not a file-like object that takes bytes.

        """

        try:
            for idx, decoded in enumerate(self.stream()):
                fp.write(decoded)
                log.debug("part-%i written to %s", idx, fp)
        except (AttributeError, TypeError) as e:
            raise TypeError(
                "'fp' is not a file-like object or it does not take bytes: %s" % str(e)
            )

    def save(self, savefile):
        """Do the TTS API request and write result to file.

        Args:
            savefile (string): The path and file name to save the ``mp3`` to.

        Raises:
            :class:`gTTSError`: When there's an error with the API request.

        """
        with open(str(savefile), "wb") as f:
            self.write_to_fp(f)
            f.flush()
            log.debug("Saved to %s", savefile)


class gTTSError(Exception):
    """Exception that uses context to present a meaningful error message"""

    def __init__(self, msg=None, **kwargs):
        self.tts = kwargs.pop("tts", None)
        self.rsp = kwargs.pop("response", None)
        if msg:
            self.msg = msg
        elif self.tts is not None:
            self.msg = self.infer_msg(self.tts, self.rsp)
        else:
            self.msg = None
        super(gTTSError, self).__init__(self.msg)

    def infer_msg(self, tts, rsp=None):
        """Attempt to guess what went wrong by using known
        information (e.g. http response) and observed behaviour

        """
        cause = "Unknown"

        if rsp is None:
            premise = "Failed to connect"

            if tts.tld != "com":
                host = _translate_url(tld=tts.tld)
                cause = "Host '{}' is not reachable".format(host)

        else:
            # rsp should be <requests.Response>
            # http://docs.python-requests.org/en/master/api/
            status = rsp.status_code
            reason = rsp.reason

            premise = "{:d} ({}) from TTS API".format(status, reason)

            if status == 403:
                cause = "Bad token or upstream API changes"
            elif status == 404 and tts.tld != "com":
                cause = "Unsupported tld '{}'".format(tts.tld)
            elif status == 200 and not tts.lang_check:
                cause = (
                    "No audio stream in response. Unsupported language '%s'"
                    % self.tts.lang
                )
            elif status >= 500:
                cause = "Upstream API error. Try again later."

        return "{}. Probable cause: {}".format(premise, cause)


from tts.basettsclass import TTSbase
from myutils.config import globalconfig, getlangsrc


class TTS(TTSbase):
    def getvoicelist(self):
        return [""]

    def speak(self, content, rate, voice, voiceidx):
        tts = gTTS(content, lang=getlangsrc())
        fname = str(time.time())
        os.makedirs("./cache/tts/", exist_ok=True)

        tts.save("./cache/tts/" + fname + ".mp3")
        return "./cache/tts/" + fname + ".mp3"
