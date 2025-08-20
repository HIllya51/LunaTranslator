"""Module for handling template text."""

import json
import re
from itertools import chain, zip_longest

from qdarktheme._util import multi_replace


class _Placeholder:
    def __init__(self, _1, _2, _3):
        self.match_text = _1
        self.value = _2
        self.filters = _3


class Template:
    """Class that handles template text like jinja2."""

    _PLACEHOLDER_RE = re.compile(r"{{.*?}}")
    _STRING_RE = re.compile(r"""('([^'\\]*(?:\\.[^'\\]*)*)'|"([^"\\]*(?:\\.[^"\\]*)*)")""", re.S)

    def __init__(self, text: str, filters: dict):
        """Initialize Template class."""
        self._target_text = text
        self._filters = filters

    @staticmethod
    def _to_py_value(text: str):
        try:
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                return text

    @staticmethod
    def _parse_placeholders(text):
        placeholders = set()
        for match in re.finditer(Template._PLACEHOLDER_RE, text):
            match_text = match.group()
            contents, *filters = match_text.strip("{}").replace(" ", "").split("|")
            value = Template._to_py_value(contents)
            placeholders.add(_Placeholder(match_text, value, tuple(filters)))
        return placeholders

    def _run_filter(self, value, filter_text):
        contents = filter_text.split("(")
        if len(contents) == 1:
            return self._filters[contents[0]](value)

        filter_name, arg_text = contents
        py_strings = [match.group() for match in Template._STRING_RE.finditer(arg_text)]
        if len(py_strings) == 0:
            json_text = '{"' + arg_text.replace("=", '":').replace(",", ',"').replace(")", "}")
        else:
            py_strings_escaped = [re.escape(py_string) for py_string in py_strings]
            words = re.split("|".join(py_strings_escaped), arg_text)
            words = [word.replace("=", '":').replace(",", ',"').replace(")", "}") for word in words]
            json_text = '{"' + "".join(
                chain.from_iterable(zip_longest(words, py_strings, fillvalue=""))
            )
        arguments = json.loads(json_text)
        return self._filters[filter_name](value, **arguments)

    def render(self, replacements) -> str:
        """Render replacements."""
        placeholders = Template._parse_placeholders(self._target_text)
        new_replacements = {}
        for placeholder in placeholders:
            value = placeholder.value
            if type(value) is str and len(value) != 0:
                value = replacements.get(value)
            if value is None:
                raise AssertionError(
                    "There is no replacements for: {} in {}".format(placeholder.value, placeholder.match_text)
                )
            for filter in placeholder.filters:
                value = self._run_filter(value, filter)
            new_replacements[placeholder.match_text] = str(value)
        return multi_replace(self._target_text, new_replacements)
