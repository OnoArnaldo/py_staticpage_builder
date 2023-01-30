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


RE_COMMENT_ONELINE = _re.compile(r'<!--[\s\S]*-->')
RE_COMMENT_MULTI_OPEN = _re.compile(r'<!--[\s\S]*')
RE_COMMENT_MULTI_CLOSE = _re.compile(r'[\s\S]*-->')


def remove_comments(lines: _.Iterable[str]) -> _.Generator[str, None, None]:
    multi = False
    for line in lines:
        if multi:
            if len(RE_COMMENT_MULTI_CLOSE.findall(line)) != 0:
                yield RE_COMMENT_MULTI_CLOSE.subn('', line)[0]
                multi = False
            else:
                yield ''
        else:
            if len(RE_COMMENT_ONELINE.findall(line)) != 0:
                line = RE_COMMENT_ONELINE.subn('', line)[0]

            if len(RE_COMMENT_MULTI_OPEN.findall(line)) != 0:
                multi = True
                line = RE_COMMENT_MULTI_OPEN.subn('', line)[0]

            yield line


def minify(lines: _.Iterable[str]) -> _.Generator[str, None, None]:
    yield from remove_blank_lines(
        trim_lines(
            remove_repeated_spaces(
                remove_comments(lines)
            )
        )
    )
