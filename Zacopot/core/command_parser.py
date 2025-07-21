from typing import Tuple

from core.filesystem import FileSystem


def get_quoted_arguments(command: str) -> tuple[str, list[str]]:
    args = []
    rest_comm = ''
    i = 0
    while i < len(command):
        if command[i] in ('"', "'"):
            quote = command[i]
            end = command.find(quote, i + 1)
            if end != -1:
                part = command[i + 1:end]
                args.append(part)
                i = end
            else:
                rest_comm += command[i]
        else:
            rest_comm += command[i]
        i += 1
    return rest_comm.strip(), args


def command_parser(filesystem: FileSystem, command: str) -> str:
    rest_command, args = get_quoted_arguments(command)
    parts = rest_command.split()

    input_options = ''
    long_options = {}
    for part in parts[1:]:
        if part.startswith('--'):  # is long option, value is expected
            option_value = part.split('=', maxsplit=1)
            if len(option_value) == 2:      # check if a value is assigned
                option, value = option_value[::]
                long_options[option[2:]] = value
        elif part.startswith('-'):
            input_options += part[1:]
        else:
            args.append(part)

    def option_check(command_options: str, command_long_options: list[str] = None) -> tuple[None | str, None | str]:
        nonlocal input_options, long_options

        options = ''
        for op in input_options:
            if op in command_options:
                options += op
            else:
                return None, f"invalid option -- '{op}'"

        if command_long_options:  # validate long options if any
            for op in long_options.keys():
                if op not in command_long_options:
                    return None, f"invalid option -- '{op}'"

        return options, None

    output = None

    if len(parts) > 0:
        match parts[0]:
            case 'echo':
                output = filesystem.echo(parts[1:])
            case 'ls':
                option, error = option_check('alis', ['time'])
                if error:
                    output = f"{parts[0]}: {error}\r\nTry '{parts[0]} --help' for more information."
                else:
                    output = filesystem.ls(option, long_options, args)

            case 'mkdir':
                output = filesystem.mkdir(args)

            case 'cd':
                args = None if len(args) == 0 else args[0]
                output = filesystem.cd(args)

            case 'touch':
                option, error = option_check('am')
                if error:
                    output = f"{parts[0]}: {error}\r\nTry '{parts[0]} --help' for more information."
                else:
                    output = filesystem.touch(option if option != '' else None, args)

            case 'cat':
                output = filesystem.cat(args)

            case 'rm':
                option, error = option_check('r')
                if error:
                    output = f"{parts[0]}: {error}\r\nTry '{parts[0]} --help' for more information."
                else:
                    output = filesystem.rm(option, args)
            case 'pwd':
                output = filesystem.pwd()
            case 'path':
                output = filesystem.path()
            case 'home':
                output = filesystem.home()
            case 'user':
                output = filesystem.user()
            case 'hostname':
                output = filesystem.hostname()
            case 'lang':
                output = filesystem.lang()
            case '':
                output = ''
            case 'exit':
                output = 'exit'
            case _:
                output = f'bash: {command}: command not found'

    return output if output is not None else ''
