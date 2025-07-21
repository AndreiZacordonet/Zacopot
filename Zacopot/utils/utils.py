from models.models import Inode, Directory
from exceptions.fsExceptions import DirNotFoundException, BlockSizeExceededException
from utils.constants import BLOCK_SIZE, DISK_FILE_NAME


def format_object(inode_obj: Directory | Inode,
                  file_name: str,
                  inodes: dict[int, Inode | Directory],
                  total_blocks: list[int],
                  options: str | None = '',
                  long_options: dict[str, str] | None = None
                  ) -> str:
    output = ''

    format_options = ''

    show_hidden = False
    separator = '\t'

    opt_separator = '' if options == '' else ' '

    for op in options:
        match op:
            case 'a':
                show_hidden = True
            case 'i':
                format_options += 'i,'
            case 'l':
                if long_options:
                    if long_options['time'] in ('ctime', 'status'):
                        format_options += 'fp,l,o,g,s,tm,'
                    elif long_options['time'] in ('birth', 'creation'):
                        format_options += 'fp,l,o,g,s,tc,'
                    else:
                        format_options += 'fp,l,o,g,s,ta,'
                else:
                    format_options += 'fp,l,o,g,s,ta,'
                separator = '\r\n'
            case 's':
                format_options += 'bn,'

    format_options = format_options.rstrip(',')  # remove the last ','

    if inode_obj.file_type == 0:  # print file inode data
        output += f"{inode_obj:{format_options}}{opt_separator}{file_name}{separator}"

    elif inode_obj.file_type == 1:  # is dir
        for name in sorted(inode_obj.list_filenames()):
            if not show_hidden and name.startswith('.'):
                continue
            file_inode_num = inode_obj.get_inode(name)
            file_inode_obj = inodes[file_inode_num]
            total_blocks[0] += len(file_inode_obj)
            output += f"{file_inode_obj:{format_options}}{opt_separator}{name}{separator}"

    return output


def getPath(current_dir_inode: int, inodes: dict[int: Directory]) -> str:
    """Returns the path to the current directory"""

    if inodes[current_dir_inode].dirname == "/":
        return "/"

    path = ''

    while inodes[current_dir_inode].dirname != "/":
        path = inodes[current_dir_inode].dirname + "/" + path

        current_dir_inode = inodes[current_dir_inode].get_inode("..")

    return '/' + path


def getInode(path: str, root_inode: int, current_dir_inode: int, inodes: dict[int: Directory]) -> int:
    """Returns the inode to the specified directory or file \n
    :raises DirNotFoundException"""

    # dot and dotdot directories
    match path:
        case ".":
            return current_dir_inode
        case "..":
            return inodes[current_dir_inode].get_inode("..")
        case _ if path in ('', '/'):  # root inode
            return root_inode

    # single-level relative path
    direct_inode = inodes[current_dir_inode].get_inode(path)
    if direct_inode is not None:
        return direct_inode

    path_dirs = path.strip('/').split('/')

    # path starts from current dir or from root dir
    inode = root_inode if path.startswith('/') else current_dir_inode

    for part in path_dirs:
        inode_obj: Inode | Directory = inodes.get(inode)

        if inode_obj.file_type == 0:  # check if dir exists
            raise DirNotFoundException(f"{part} is not a directory.")

        inode = inode_obj.get_inode(part)
        if inode is None:
            raise DirNotFoundException(f"{part} not found.")

    return inode


def getParentDirInode(path: str, root_inode: int, current_dir_path: str, current_dir_inode: int,
                      inodes: dict[int: Inode | Directory]) -> Directory:
    match path:
        case _ if path.find('/') == -1:  # file is in curr dir
            parent_dir_path = current_dir_path
        case _ if '/' not in path.strip('/'):  # file in root dir
            parent_dir_path = '/'
        case _:
            parent_dir_path = path[:path.rfind('/')]

    parent_dir_inode = getInode(parent_dir_path, root_inode, current_dir_inode, inodes)
    parent_dir_inode_obj = inodes[parent_dir_inode]

    return parent_dir_inode_obj


def writeBlock(block_number: int, data: bytes) -> None:
    """Saves content into a block"""
    if len(data) > BLOCK_SIZE:
        raise BlockSizeExceededException(f"Data size {len(data)} exceeds BLOCK_SIZE size {BLOCK_SIZE}.")

    with open(DISK_FILE_NAME, 'r+b') as disk_file:
        disk_file.seek(block_number * BLOCK_SIZE)
        disk_file.write(data)


def readBlock(block_number: int) -> bytes:
    """Read block content"""
    with open(DISK_FILE_NAME, 'rb') as disk_file:
        disk_file.seek(block_number * BLOCK_SIZE)
        data = disk_file.read(BLOCK_SIZE)

        return data


def block_iter(input_file_name: str):
    """Creates a generator object consisting of block sized data parts from the initial file"""
    with open(input_file_name, 'rb') as input_file:
        while True:
            block = input_file.read(BLOCK_SIZE)
            if not block:
                break
            yield block


# def saveFile(input_file_name: str, allocate_block) -> None:
#     """Saves file content"""
#     for block_data in block_iter(input_file_name):
#         if len(block_data) < BLOCK_SIZE:    # apply padding
#             print(len(block_data))
#             block_data = block_data.ljust(BLOCK_SIZE, b'\x00')
#             print(len(block_data))
#
#         block_number = allocate_block()
#         writeBlock(block_number, block_data)


def readFile(inode: Inode | Directory) -> bytes:
    """Read file content"""
    content = b''

    for block_number in inode.blocks:
        content += readBlock(block_number)

    return content[:inode.size]
