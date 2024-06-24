"""Snr shell commands lexer
"""
import pygments.lexer
import pygments.token

__all__ = (
    "SnrLexer",
)

CHECKSUM_ALGORITHMS = (
    "blake2b", "md5", "sha1",
    "sha224", "sha256", "sha384", "sha512"
)


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
        ],
        'basic': [
            (r'(?<!\\)\$\w+', pygments.token.Name.Variable),
            (r'\b\d+\b', pygments.token.Number),
            (r'\s', pygments.token.Whitespace),
            (r'(?<!\!).+', pygments.token.Text),
        ],
        'pwd': [
            (r'(\s*)(pwd)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'chdir': [
            (r'(\s*)(chdir)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
        ],
        'list': [
            (r'(\s*)(list)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
            (r'(\s*)(list)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'read': [
            (r'(\s*)(read)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
        ],
        'checksum': [
            (r'(\s*)(checksum)(\s+)' + f"({'|'.join(CHECKSUM_ALGORITHMS)})" + r'(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
                 pygments.token.Keyword.Constant,
                 pygments.token.Whitespace,
             ), 'basic'),
        ],
        'unset': [
            (r'(\s*)(unset)(\s+)(\w+)(\s*)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
                 pygments.token.Name.Variable,
                 pygments.token.Whitespace
             ), 'eoc'),
        ],
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
            # Set normal assignment
            (r'(\s*)(set)(\s+)(\w+)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
                 pygments.token.Name.Variable,
                 pygments.token.Whitespace,
             ), 'basic'),
            # Set remove variable
            (r'(\s*)(set)(\s+)(\w+)(\s*)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
                 pygments.token.Name.Variable,
                 pygments.token.Whitespace
             ), 'eoc'),
            # Set list variables
            (r'(\s*)(set)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'use': [
            # Use while loading
            (r'(\s*)(use)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
            # Use while unloading
            (r'(\s*)(use)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'generate': [
            (r'(\s*)(generate)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
        ],
        'clear': [
            (r'(\s*)(clear)',
             pygments.lexer.bygroups(
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'echo': [
            # echo with value
            (r'(\s*)(echo)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
            # echo without value
            (r'(\s*)(echo)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'exit': [
            # exit with value
            (r'(\s*)(exit)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
            # exit without value
            (r'(\s*)(exit)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword
             ), 'eoc'),
        ],
        'help': [
            # help with value
            (r'(\s*)(help)(\s+)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
                 pygments.token.Whitespace,
             ), 'basic'),
            # help without value
            (r'(\s*)(help)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'info': [
            (r'(\s*)(info)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'pdb': [
            (r'(\s*)(pdb)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ],
        'reload': [
            (r'(\s*)(reload)',
             pygments.lexer.bygroups(
                 pygments.token.Whitespace,
                 pygments.token.Keyword,
             ), 'eoc'),
        ]
    }
