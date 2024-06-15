# -*- coding: utf-8 -*-
import base64
import json, time
import logging, os
import re
import urllib
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
    langs = dict()
    langs.update(_main_langs())
    langs.update(_extra_langs())
    log.debug("langs: {}".format(langs))
    return langs


def _extra_langs():
    return {
        # Chinese
        "zh-TW": "Chinese (Mandarin/Taiwan)",
        "zh": "Chinese (Mandarin)",
    }


def _fallback_deprecated_lang(lang):
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

    def __init__(self, search_args, search_func, repl, flags=0):
        self.repl = repl

        # Create regex list
        self.regexes = []
        for arg in search_args:
            rb = RegexBuilder([arg], search_func, flags)
            self.regexes.append(rb.regex)

    def run(self, text):
        for regex in self.regexes:
            text = regex.sub(self.repl, text)
        return text

    def __repr__(self):  # pragma: no cover
        subs_strs = []
        for r in self.regexes:
            subs_strs.append("({}, repl='{}')".format(r, self.repl))
        return ", ".join(subs_strs)


class PreProcessorSub:
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
        for pp in self.pre_processors:
            text = pp.run(text)
        return text

    def __repr__(self):  # pragma: no cover
        return ", ".join([str(pp) for pp in self.pre_processors])


class Tokenizer:
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
        return self.total_regex.split(text)

    def __repr__(self):  # pragma: no cover
        return str(self.total_regex) + " from: " + str(self.regex_funcs)


class tokenizer_cases:

    def tone_marks():
        return RegexBuilder(
            pattern_args=symbols.TONE_MARKS, pattern_func=lambda x: "(?<={}).".format(x)
        ).regex

    def period_comma():
        return RegexBuilder(
            pattern_args=symbols.PERIOD_COMMA,
            pattern_func=lambda x: r"(?<!\.[a-z]){} ".format(x),
        ).regex

    def colon():
        return RegexBuilder(
            pattern_args=symbols.COLON, pattern_func=lambda x: r"(?<!\d){}".format(x)
        ).regex

    def other_punctuation():
        punc = "".join(
            set(symbols.ALL_PUNC)
            - set(symbols.TONE_MARKS)
            - set(symbols.PERIOD_COMMA)
            - set(symbols.COLON)
        )
        return RegexBuilder(
            pattern_args=punc, pattern_func=lambda x: "{}".format(x)
        ).regex

    def legacy_all_punctuation():
        punc = symbols.ALL_PUNC
        return RegexBuilder(
            pattern_args=punc, pattern_func=lambda x: "{}".format(x)
        ).regex


class pre_processors:

    def tone_marks(text):
        return PreProcessorRegex(
            search_args=symbols.TONE_MARKS,
            search_func=lambda x: "(?<={})".format(x),
            repl=" ",
        ).run(text)

    def end_of_line(text):
        return PreProcessorRegex(
            search_args="-", search_func=lambda x: "{}\n".format(x), repl=""
        ).run(text)

    def abbreviations(text):
        return PreProcessorRegex(
            search_args=symbols.ABBREVIATIONS,
            search_func=lambda x: r"(?<={})(?=\.).".format(x),
            repl="",
            flags=re.IGNORECASE,
        ).run(text)

    def word_sub(text):
        return PreProcessorSub(sub_pairs=symbols.SUB_PAIRS).run(text)


punc = symbols.ALL_PUNC
from string import whitespace as ws
import re

_ALL_PUNC_OR_SPACE = re.compile("^[{}]*$".format(re.escape(punc + ws)))


def _minimize(the_string, delim, max_size):
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
    return [t.strip() for t in tokens if not _ALL_PUNC_OR_SPACE.match(t)]


def _translate_url(tld="com", path=""):
    _GOOGLE_TTS_URL = "https://translate.google.{}/{}"
    return _GOOGLE_TTS_URL.format(tld, path)


__all__ = ["gTTS", "gTTSError"]

# Logger
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Speed:
    SLOW = True
    NORMAL = None


class gTTS:
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
        ref,
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
        self.ref = ref
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
                proxies=self.ref.proxy,
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

        try:
            for idx, decoded in enumerate(self.stream()):
                fp.write(decoded)
                log.debug("part-%i written to %s", idx, fp)
        except (AttributeError, TypeError) as e:
            raise TypeError(
                "'fp' is not a file-like object or it does not take bytes: %s" % str(e)
            )

    def save(self):
        bs = b""
        for idx, decoded in enumerate(self.stream()):
            bs += decoded
        return bs


class gTTSError(Exception):
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

from myutils.utils import getlangsrc


class TTS(TTSbase):
    def getvoicelist(self):
        return [""]

    def speak(self, content, rate, voice, voiceidx):
        tts = gTTS(self, content, lang=getlangsrc())
        return tts.save()
