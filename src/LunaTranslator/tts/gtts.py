# -*- coding: utf-8 -*-
import base64
import json
import re

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


def _minimize(the_string: str, delim, max_size):
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


class Speed:
    SLOW = True
    NORMAL = None


from tts.basettsclass import TTSbase, SpeechParam, TTSResult


class TTS(TTSbase):
    GOOGLE_TTS_MAX_CHARS = 100  # Max characters the Google TTS API takes at a time
    GOOGLE_TTS_HEADERS = {"Referer": "http://translate.google.com/"}
    GOOGLE_TTS_RPC = "jQ1olc"

    def init(self):
        slow = False
        pre_processor_funcs = [
            pre_processors.tone_marks,
            pre_processors.end_of_line,
            pre_processors.abbreviations,
            pre_processors.word_sub,
        ]
        tokenizer_func = (
            Tokenizer(
                [
                    tokenizer_cases.tone_marks,
                    tokenizer_cases.period_comma,
                    tokenizer_cases.colon,
                    tokenizer_cases.other_punctuation,
                ]
            ).run,
        )
        # Debug
        for k, v in dict(locals()).items():
            if k == "self":
                continue

        # Pre-processors and tokenizer
        self.pre_processor_funcs = pre_processor_funcs
        self.tokenizer_func = tokenizer_func

    def _tokenize(self, text: str):
        # Pre-clean
        text = text.strip()

        # Apply pre-processors
        for pp in self.pre_processor_funcs:
            text = pp(text)

        if len(text) <= self.GOOGLE_TTS_MAX_CHARS:
            return _clean_tokens([text])

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

    def _prepare_requests(self, text, slow):
        translate_url = _translate_url(
            tld="com", path="_/TranslateWebserverUi/data/batchexecute"
        )

        text_parts = self._tokenize(text)
        for part in text_parts:
            data = self._package_rpc(part, slow)

            # Request
            r = self.proxysession.post(
                url=translate_url,
                data=data,
                headers=self.GOOGLE_TTS_HEADERS,
            )

            yield r

    def langdetect(self, text):
        param = json.dumps([[text, self.srclang, self.tgtlang, True], [1]])
        freq = json.dumps([[["MkEWBc", param, None, "generic"]]])
        freq = {"f.req": freq}

        headers = {
            "Origin": "https://translate.google.com",
            "Referer": "https://translate.google.com",
            "X-Requested-With": "XMLHttpRequest",
        }

        response = self.proxysession.post(
            "https://translate.google.com/_/TranslateWebserverUi/data/batchexecute",
            verify=False,
            headers=headers,
            data=freq,
        )
        json_data = json.loads(response.text[6:])
        data = json.loads(json_data[0][2])
        return data[0][2]

    def _package_rpc(self, text, slow):

        speed = (Speed.NORMAL, Speed.SLOW)[slow]
        srclang = self.langdetect(text) if self.is_src_auto else self.srclang
        parameter = [text, srclang, speed, "null"]
        escaped_parameter = json.dumps(parameter, separators=(",", ":"))

        rpc = [[[self.GOOGLE_TTS_RPC, escaped_parameter, None, "generic"]]]
        espaced_rpc = json.dumps(rpc, separators=(",", ":"))
        return {"f.req": espaced_rpc}

    def stream(self, content, slow):

        prepared_requests = self._prepare_requests(content, slow)
        for r in prepared_requests:

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
                        raise Exception(r)

    def getvoicelist(self):
        return [""], [""]

    def speak(self, content, _, speed: SpeechParam):
        return TTSResult(
            b"".join(self.stream(content, speed.speed < 0)), type="audio/mpeg"
        )

    def ttscachekey(self, *argc):
        return self.srclang, super().ttscachekey(*argc)
