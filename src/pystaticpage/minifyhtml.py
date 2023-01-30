import typing as _
import re as _re


def remove_blank_lines(lines: _.Iterable[str]) -> _.Generator[str, None, None]:
    for line in lines:
        if line != '':
            yield line


def trim_lines(lines: _.Iterable[str]) -> _.Generator[str, None, None]:
    for line in lines:
        yield line.strip()


RE_SPACES = _re.compile(r'\s+')


def remove_repeated_spaces(lines: _.Iterable[str]) -> _.Generator[str, None, None]:
    for line in lines:
        yield RE_SPACES.subn(' ', line)[0]


def minify(lines: _.Iterable[str]) -> _.Generator[str, None, None]:
    yield from remove_blank_lines(
        trim_lines(
            remove_repeated_spaces(lines)
        )
    )
