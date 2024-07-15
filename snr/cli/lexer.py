"""Snr shell commands lexer
"""
from typing import Any

import pygments.lexer
import pygments.token

__all__ = (
    "SnrLexer",
)

CHECKSUM_ALGORITHMS = (
    "blake2b", "md5", "sha1",
    "sha224", "sha256", "sha384", "sha512"
)

# pylint: disable=consider-using-f-string


def command_no_args(x: str) -> dict[str, list[tuple[str, Any, str]]]:
    return {x: [
        (r'(\s*)({0})'.format(x),
         pygments.lexer.bygroups(
            pygments.token.Whitespace,
            pygments.token.Keyword),
         'eoc')
    ]}


def command_args(x: str) -> dict[str, list[tuple[str, Any, str]]]:
    return {x: [
        (r'(\s*)({0})(\s+)'.format(x),
         pygments.lexer.bygroups(
            pygments.token.Whitespace,
            pygments.token.Keyword,
            pygments.token.Whitespace,
        ), 'basic')
    ]}


def command_key_no_args(x: str, keywords: tuple[str, ...]) -> dict[str, list[tuple[str, Any, str]]]:
    return {x: [
        (r'(\s*)({0})(\s+)({1})'.format(x, keywords),
         pygments.lexer.bygroups(
             pygments.token.Whitespace,
             pygments.token.Keyword,
             pygments.token.Whitespace,
             pygments.token.Keyword.Constant,
        ), 'eoc')
    ]}


def command_key_args(x: str, keywords: tuple[str, ...]) -> dict[str, list[tuple[str, Any, str]]]:
    return {x: [
        (r'(\s*)({0})(\s+)({1})(\s+)'.format(x, "|".join(keywords)),
         pygments.lexer.bygroups(
             pygments.token.Whitespace,
             pygments.token.Keyword,
             pygments.token.Whitespace,
             pygments.token.Keyword.Constant,
             pygments.token.Whitespace
        ), 'basic')
    ]}


SYNTAX = {
    **command_no_args('pwd'),
    **command_args("chdir"),
    **command_args("list"),
    **command_args("read"),
    **command_key_args("checksum", CHECKSUM_ALGORITHMS),
    **command_args("unset"),
    # Special case
    'set': [
        # Set assign to command output
        (r'(\s*)(set)(\s+)(!)(\w+)(\s+)',
         pygments.lexer.bygroups(
             pygments.token.Whitespace,
             pygments.token.Keyword,
             pygments.token.Whitespace,
             pygments.token.Operator,
             pygments.token.Name.Variable,
             pygments.token.Whitespace,
         ), 'commands'),
        # Set assign to value
        (r'(\s*)(set)(\s+)(\w+)(\s+)',
         pygments.lexer.bygroups(
             pygments.token.Whitespace,
             pygments.token.Keyword,
             pygments.token.Whitespace,
             pygments.token.Name.Variable,
             pygments.token.Whitespace,
         ), 'basic'),
        *command_args("set")["set"]
    ],
    **command_args("use"),
    **command_args("generate"),
    **command_no_args("clear"),
    **command_args("echo"),
    **command_args("exit"),
    **command_args("help"),
    **command_no_args("info"),
    **command_no_args("pdb"),
    **command_no_args("reload")
}


class SnrLexer(pygments.lexer.RegexLexer):  # type: ignore
    """Lexer for snr shell commands"""
    name = 'SnrLexer'

    tokens = {
        'root': [
            pygments.lexer.include('commands')
        ],
        'commands': [
            pygments.lexer.include('pwd'),
            pygments.lexer.include('chdir'),
            pygments.lexer.include('list'),
            pygments.lexer.include('read'),
            pygments.lexer.include('checksum'),
            pygments.lexer.include('unset'),
            pygments.lexer.include('set'),
            pygments.lexer.include('use'),
            pygments.lexer.include('generate'),
            pygments.lexer.include('clear'),
            pygments.lexer.include('echo'),
            pygments.lexer.include('exit'),
            pygments.lexer.include('help'),
            pygments.lexer.include('info'),
            pygments.lexer.include('pdb'),
            pygments.lexer.include('reload')
        ],
        'eoc': [
            (r'\s', pygments.token.Whitespace),
            (r'#.*$', pygments.token.Comment.Single),
            (r'\S+', pygments.token.Error)
        ],
        'basic': [
            (r'(?<!\\)\$\w+', pygments.token.Name.Variable),
            (r'\b\d+\b', pygments.token.Number),
            (r'\s', pygments.token.Whitespace),
            (r'(?<!\!).+', pygments.token.Text),
        ],
        **SYNTAX
    }
