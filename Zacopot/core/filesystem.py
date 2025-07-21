# File System DS --------------------------------------------------------------
import os
from datetime import datetime

from models.models import Inode, Directory
from utils.utils import format_object, getInode, getPath, block_iter, writeBlock, readFile, getParentDirInode
from utils.constants import BLOCK_SIZE, TOTAL_BLOCKS, TOTAL_INODES
from exceptions.fsExceptions import *


# class CustomDS:
#     """Custom data structure for associating files with its inode numbers. \n
#     Each directory contains one"""
#
#     __slots__ = "ds"
#
#     def __init__(self, dot_inode: int, dotdot_inode: int):
#         self.ds = {}
#         self.add(".", dot_inode)
#         self.add("..", dotdot_inode)
#
#     def add(self, filename: str, inode_number: int):
#         if filename not in self.ds.keys():
#             self.ds[filename] = inode_number
#         else:
#             raise ValueError(f"`{filename}` already exists.")
#
#     def remove(self, filename: str):
#         if filename in self.ds.keys():
#             self.ds.pop(filename)
#         else:
#             raise ValueError(f"`{filename}` does not exist.")
#
#     def get_inode(self, filename: str) -> int | None:
#         return self.ds.get(filename, None)
#
#     def list_filenames(self) -> set[str]:
#         return set(self.ds.keys())
#
#     def list_inode_numbers(self) -> set[int]:
#         return set(self.ds.values())


# Super block -----------------------------------------------------------------

class Superblock:
    __slots__ = ("total_blocks", "total_inodes", "free_blocks", "free_inodes")

    def __init__(self, total_blocks=TOTAL_BLOCKS, total_inodes=TOTAL_INODES):
        self.total_blocks = total_blocks
        self.total_inodes = total_inodes
        self.free_blocks = set(range(1, total_blocks + 1))
        self.free_inodes = set(range(1, total_inodes + 1))

    def allocate_block(self) -> int | None:
        return self.free_blocks.pop() if self.free_blocks else None

    def allocate_inode(self) -> int | None:
        return self.free_inodes.pop() if self.free_inodes else None

    def free_block(self, block_number: int):
        self.free_blocks.add(block_number)

    def free_inode(self, inode_number: int):
        self.free_inodes.add(inode_number)


# Data blocks -----------------------------------------------------------------

class DataBlocks:
    __slots__ = "blocks"

    def __init__(self):
        self.blocks = {}

    def write_block(self, block_number: int, data: str):
        self.blocks[block_number] = data

    def read_block(self, block_number) -> str:
        return self.blocks.get(block_number, "")


# Journal ---------------------------------------------------------------------

class Journal:
    __slots__ = "log"

    def __init__(self):
        self.log = []

    def record(self, action, inode_number):
        self.log.append({"action": action, "inode": inode_number})

    def replay(self):
        for entry in self.log:
            print(f"Replaying: {entry}")


# File system -----------------------------------------------------------------

class FileSystem:
    __slots__ = (
        "PATH", "PWD", "HOME", "USER", "UIT", "HOSTNAME", "LANG",
        "superblock", "inodes", "directories", "journal", "root_inode",
    )

    def __init__(self):
        # Environment Variables
        self.PATH = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        self.PWD = ()
        self.HOME = 'home/admin'
        self.USER = 'root'
        self.HOSTNAME = 'debian'
        self.LANG = 'en_US.UTF-8'

        self.superblock = Superblock()
        self.inodes: dict[int, Inode | Directory] = {}
        # self.data_blocks = DataBlocks()
        # self.journal = Journal()

        self.root_inode = self.superblock.allocate_inode()
        self.inodes[self.root_inode] = Directory("/", self.root_inode, self.root_inode)

        self.PWD = self.root_inode, getPath(self.root_inode, self.inodes)

    def mkdir(self, paths: list[str]) -> str | None:  # return error if any

        error = ''

        for path in paths:

            path = path.rstrip('/')  # remove last '/' if any

            try:
                if path.find('/') == -1:  # create new dir in current directory
                    dir_path = self.inodes[self.PWD[0]]
                    dirname = path
                else:
                    sep = path.rfind('/')
                    dir_path = self.inodes[getInode(path[:sep], self.root_inode, self.PWD[0], self.inodes)]
                    dirname = path[sep + 1:]

                if dirname in dir_path.list_filenames():  # check if dir with this name already exists
                    error = f"mkdir: cannot create directory '{path}': File exists"
                    continue

                new_dir_inode = self.superblock.allocate_inode()

                if new_dir_inode is None:  # inode allocation DIDNT work
                    error = "Inode cannot be allocated."
                    continue

                new_dir = Directory(dirname, new_dir_inode, dir_path.inode_number)

                self.inodes[new_dir_inode] = new_dir  # add new dir to dir list

                dir_path.add(dirname, new_dir_inode)

            except DirNotFoundException:
                error = f"mkdir: cannot create directory '{path}': No such file or directory"

        return error

    def saveFile(self, path: str, input_file_name: str) -> None:
        """Saves file content"""
        self.touch(None, [input_file_name])
        inode_obj = self.inodes[getInode(input_file_name, self.root_inode, self.PWD[0], self.inodes)]
        inode_obj.size = os.stat(path).st_size

        for block_data in block_iter(path):
            if len(block_data) < BLOCK_SIZE:  # apply padding
                block_data = block_data.ljust(BLOCK_SIZE, b'\x00')

            block_number = self.superblock.allocate_block()
            inode_obj.blocks.append(block_number)
            writeBlock(block_number, block_data)

    def deleteFile(self, inode_obj: Inode, parent_dir_obj: Directory) -> None:
        if inode_obj.file_type == 1:    # is a dir
            return

        # free blocks
        for block in inode_obj.blocks:
            self.superblock.free_block(block)

        # free inode number
        self.superblock.free_inode(inode_obj.inode_number)

        # delete entry from parent directory
        parent_dir_obj.remove_by_inode(inode_obj.inode_number)

        # delete from filesystem inodes dict
        self.inodes.pop(inode_obj.inode_number)

    def deleteDir(self, dir_inode_obj: Directory, parent_dir_obj: Directory):

        if dir_inode_obj.inode_number in (self.root_inode, self.PWD[0]):    # dont delete root or current dir
            return

        stack = [(parent_dir_obj, dir_inode_obj)]

        def getEmptiedChildDirs(inode_obj: Directory) -> list[tuple[Directory, Directory]] | None:
            nonlocal self

            child_dirs = []

            for name, inode_num in list(inode_obj.entries.items()):
                if name in ('.', '..'):
                    continue
                child_inode_obj = self.inodes[inode_num]
                if child_inode_obj.file_type == 1:
                    child_dirs.append((inode_obj, child_inode_obj))
                else:  # is a file
                    self.deleteFile(child_inode_obj, inode_obj)

            return child_dirs if len(child_dirs) != 0 else None

        if child_dirs := getEmptiedChildDirs(dir_inode_obj):
            stack.extend(child_dirs)

        while stack:

            parent_inode_obj, inode_obj = stack.pop()

            if inode_obj.inode_number in (self.root_inode, self.PWD[0]):  # dont delete root or current dir
                return

            if child_dirs := getEmptiedChildDirs(inode_obj):
                stack.extend(child_dirs)
            else:
                # delete dot and dotdot dirs
                inode_obj.remove('.')
                inode_obj.remove('..')

                # delete entry from parent directory
                parent_inode_obj.remove_by_inode(inode_obj.inode_number)

                # remove from fs inodes dict
                self.inodes.pop(inode_obj.inode_number)

                # free inode number
                self.superblock.free_inode(inode_obj.inode_number)

    def ls(self,
           options: str = '',
           long_options: dict[str, str] | None = None,
           paths: list[str] | None = None,
           ) -> str | None:

        paths = paths or (self.PWD[1],)

        output = ''
        error = ''

        files = []
        directories = []

        count_blocks = ('l' in options) or ('s' in options)  # block count is enabled
        total_blocks = [0]

        for path in paths:

            try:
                inode_num = getInode(path, self.root_inode, self.PWD[0], self.inodes)
                inode_obj = self.inodes[inode_num]

                if inode_obj.file_type == 0:
                    files.append((path, inode_obj))
                else:
                    directories.append((path, inode_obj))

            except DirNotFoundException:
                error += f"ls: cannot access '{path}': No such file or directory\r\n"

        for path, inode_obj in files:
            output += format_object(inode_obj, path, self.inodes, total_blocks, options, long_options)

        for path, inode_obj in directories:
            if len(paths) > 1:  # only print header if multiple paths were given
                output += f"\r\n\r\n{path}:\r\n"
            output += format_object(inode_obj, path, self.inodes, total_blocks, options, long_options)

        output = output.lstrip('\r\n').rstrip('\r\n')  # cleanup leading/trailing newlines and spaces

        output = (error + output).rstrip('\r\n\t')

        if count_blocks and error == '':
            output = f'total {total_blocks[0]}\r\n' + output

        return output

    def cd(self, path: str | None) -> str:  # returns error

        if path is None:      # check if path exists
            return ''

        try:
            inode = getInode(path, self.root_inode, self.PWD[0], self.inodes)

            if self.inodes[inode].file_type == 0:  # check if it's a file
                return f"bash: cd: {path}: not a directory"

            self.PWD = inode, getPath(inode, self.inodes)

        except DirNotFoundException:
            return f"bash: cd: {path}: No such file or directory"

    def touch(self, options: str | None, paths: list[str]) -> str | None:  # return error if any

        error = ''

        for path in paths:

            try:
                if path.find('/') == -1:  # is just a file
                    dir_path = self.inodes[self.PWD[0]]
                    filename = path
                else:  # is a full path
                    sep = path.rfind('/')
                    dir_path = self.inodes[getInode(path[:sep], self.root_inode, self.PWD[0], self.inodes)]
                    filename = path[sep + 1:]

                if filename in dir_path.list_filenames():  # check if file with this name already exists
                    if options is None:     # check options to exist
                        options = 'am'

                    file_inode_obj = self.inodes[dir_path.get_inode(filename)]

                    time = datetime.now()

                    match options:
                        case _ if 'a' in options:
                            # change access time
                            file_inode_obj.timestamps['accessed'] = time
                        case _ if 'm' in options:
                            # change modification time
                            file_inode_obj.timestamps['modified'] = time
                    continue

                new_inode = self.superblock.allocate_inode()

                if new_inode is None:  # inode allocation DIDNT work
                    error = "Inode cannot be allocated."
                    continue

                self.inodes[new_inode] = Inode(new_inode, 0)

                dir_path.add(filename, new_inode)
                dir_path.size += 16 + len(filename) // 2  # add entry size

            except DirNotFoundException:
                error = f"touch: cannot touch '{path}': Not a directory"

        return error

    def cat(self, paths: list[str]) -> str:

        output = ''

        for index, path in enumerate(paths):
            try:
                inode_obj = self.inodes[getInode(path, self.root_inode, self.PWD[0], self.inodes)]

                if inode_obj.file_type == 1:    # is a directory
                    if index == 0:         # is the first path in arguments
                        output = f'cat: {path}: Is a directory'
                    break

                file_data = readFile(inode_obj).decode("utf-8")

                if file_data:
                    output += file_data + '\r\n'

            except DirNotFoundException:
                if index == 0:  # is the first path in arguments
                    output = f"cat: '{path}': No such file or directory"
                break
            except UnicodeDecodeError:
                output = ''
                break

        return output.rstrip()

    def rm(self, options: str | None, paths: list[str]) -> str:
        output = ''

        for index, path in enumerate(paths):
            try:
                inode_obj = self.inodes[getInode(path, self.root_inode, self.PWD[0], self.inodes)]

                parent_dir_obj = getParentDirInode(path, self.root_inode, self.PWD[1], self.PWD[0], self.inodes)

                if inode_obj.file_type == 1:    # is a directory
                    if 'r' in options:
                        if path in ('.', '..'):
                            if index == 0:
                                output = 'rm: "." and ".." may not be removed'
                            break
                        self.deleteDir(inode_obj, parent_dir_obj)
                        continue
                    else:
                        if index == 0:  # is the first path in arguments
                            output = f'rm: {path}: Is a directory'
                        break

                # delete file
                self.deleteFile(inode_obj, parent_dir_obj)

            except DirNotFoundException:
                if index == 0:  # is the first path in arguments
                    output = f"rm: '{path}': No such file or directory"
                break

        return output

    def echo(self, input_text: list[str]) -> str:
        return ' '.join(input_text)

    def cp(self):
        pass

    def pwd(self):
        return self.PWD[1]

    def path(self):
        return self.PATH

    def home(self):
        return self.HOME

    def user(self):
        return self.USER

    def hostname(self):
        return self.HOSTNAME

    def lang(self):
        return self.LANG
