"""Utility methods for qdarktheme."""

import operator as ope
import re
from pathlib import Path
from collections import OrderedDict

# greater_equal and less_equal must be evaluated before greater and less.
_OPERATORS = OrderedDict(
    [
        ("==", ope.eq),
        ("!=", ope.ne),
        (">=", ope.ge),
        ("<=", ope.le),
        (">", ope.gt),
        ("<", ope.lt),
    ]
)


def multi_replace(target, replacements) -> str:
    """Given a string and a replacement map, it returns the replaced string.

    See https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729.

    Args:
        target: String to execute replacements on.
        replacements: Replacement dictionary {value to find: value to replace}.

    Returns:
        str: Target string that replaced with `replacements`.
    """
    if len(replacements) == 0:
        return target

    replacements_sorted = sorted(replacements, key=len, reverse=True)
    replacements_escaped = [re.escape(i) for i in replacements_sorted]
    pattern = re.compile("|".join(replacements_escaped))
    return pattern.sub(lambda match: replacements[match.group()], target)



import os


def get_cash_root_path(version) -> Path:
    """Return the cash root dir path."""
    return Path(os.path.dirname(__file__)) / "svg" / "v{}".format(version)



def _compare_v(v1, operator, v2) -> bool:
    """Comparing two versions."""
    v1_list, v2_list = (tuple(map(int, (v.split(".")))) for v in (v1, v2))
    return _OPERATORS[operator](v1_list, v2_list)


def analyze_version_str(target_version, version_text) -> bool:
    """Analyze text comparing versions."""
    for operator in _OPERATORS:
        if operator not in version_text:
            continue
        version = version_text.replace(operator, "")
        return _compare_v(target_version, operator, version)
    raise AssertionError("Text comparing versions is wrong.")
