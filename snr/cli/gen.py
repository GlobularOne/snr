"""
Non-interactive interface for snr
"""

import click
from snr.cli import interactive_shell, main as cli_main

# pylint: disable=protected-access


def _filter_out_params(params: list[click.Parameter]) -> list[click.Parameter]:
    new_params = []
    for param in params:
        keep = True
        for opt in param.opts:
            if opt in ("--init", "--reinit", "--init-only", "--init-if-needed"):
                keep = False
        if keep:
            new_params.append(param)
    return new_params


def main() -> None:
    """Main function of snrgen"""
    payload_option = click.Option(["--payload", "-p"],
                                  required=True,
                                  help="Payload to load")
    define_option = click.Option(["--define", "-d", "defines"],
                                 multiple=True,
                                 help="Variables to define")
    output_option = click.Option(["--output", "-o"],
                                 required=True,
                                 help="Output file or device")
    # First patch up both main and interactive_shell to ensure they don't parse options they are not meant
    cli_main._main.params = [payload_option, define_option, output_option,
                             *_filter_out_params(cli_main._main.params)]
    interactive_shell.interactive_shell.params = [payload_option, define_option, output_option,
                                                  *_filter_out_params(interactive_shell.interactive_shell.params)]
    cli_main._main.help = "Non-interactive interface to snr"
    cli_main.main()



if __name__ == "__main__":
    main()
