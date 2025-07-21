import os

from core.filesystem import FileSystem


# def fs_loader(filesystem: FileSystem, fs_source: str):
#     """Generates a FileSystem object based on specifications included in a file"""
#     with open(fs_source) as file:
#
#         prev_tab_count = 0
#         prev_dir_name = ''
#
#         for line_number, line in enumerate(file, 1):
#
#             if line.startswith('#') or line.isspace():
#                 continue
#
#             cur_tab_count = len(line) - len(line.lstrip('\t'))
#             line = line.lstrip('\t')
#
#             if cur_tab_count - prev_tab_count > 1:
#                 raise SyntaxError(f"Incorrect number of tabs at line {line_number}")
#             if cur_tab_count > prev_tab_count:
#                 filesystem.cd(prev_dir_name)
#             else:
#                 for _ in range(prev_tab_count - cur_tab_count):
#                     filesystem.cd('..')
#
#             prev_tab_count = cur_tab_count
#
#             operand, name = line.split(maxsplit=1)
#             name = name.strip()
#
#             if name == '':
#                 raise SyntaxError(f"Invalid syntax at line {line_number}: {line}")
#
#             match operand:
#                 case '-':
#                     # create new file
#                     filesystem.touch([name])
#                 case '--':
#                     # create new dir
#                     filesystem.mkdir([name])
#                     prev_dir_name = name
#                 case _:
#                     raise SyntaxError(f"Invalid syntax at line {line_number}: {line}")


def fs_loader(filesystem: FileSystem, fs_source_dir_path: str):
    """Creates dirs, files and its contents from the specified source directory"""
    obj = os.scandir(fs_source_dir_path)

    for entry in obj:
        if entry.is_dir():
            filesystem.mkdir([entry.name])
            filesystem.cd(entry.name)
            fs_loader(filesystem, entry.path)
            filesystem.cd('..')

        if entry.is_file():
            filesystem.saveFile(entry.path, entry.name)
            # saveFile(entry.path, filesystem.superblock.allocate_block)
