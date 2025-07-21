from datetime import datetime

from enum import Enum


class Inode:
    __slots__ = (
        "inode_number",
        "file_type",
        "size",
        "blocks",
        "permissions",
        "hard_links",
        "owner",
        "group",
        "timestamps",
    )

    def __init__(self, inode_number: int, file_type: int, size=0, owner: str = 'root', group: str = 'root'):
        self.inode_number = inode_number
        self.file_type = file_type  # 0 - file; 1 - dir
        self.size = size  # bytes
        self.blocks = []  # block numbers
        self.permissions = "rwxr-xr-x" if file_type == 1 else "rw-r--r--"
        self.hard_links = 2 if file_type == 1 else 1  # dir has 2 (dot and dotdot)
        self.owner = owner
        self.group = group
        self.timestamps = {
            "created": datetime.now(),
            "modified": datetime.now(),
            "accessed": datetime.now()
        }

    def __format__(self, format_spec):
        parts = set(format_spec.split(','))     # O(1) instead of O(n)

        info = {
            'i': lambda align: f'{self.inode_number}' if not align else f'{self.inode_number:>6}',
            'bn': lambda align: f'{len(self.blocks)}' if not align else f'{len(self.blocks)}',
            'f': lambda align: 'd' if self.file_type == 1 else '-',
            'p': lambda align: self.permissions,
            'fp': lambda align: 'd' + self.permissions if self.file_type == 1 else '-' + self.permissions,
            'l': lambda align: f'{self.hard_links}' if not align else f'{self.hard_links:>2}',
            'o': lambda align: self.owner if not align else f'{self.owner:<8}',
            'g': lambda align: self.group if not align else f'{self.group:<8}',
            's': lambda align: f'{self.size}' if not align else f'{self.size:>7}',
            'tc': lambda align: self.timestamps['created'].strftime('%b %d %H:%M'),
            'tm': lambda align: self.timestamps['modified'].strftime('%b %d %H:%M'),
            'ta': lambda align: self.timestamps['accessed'].strftime('%b %d %H:%M'),
        }

        output = []

        for i, (key, func) in enumerate(info.items()):
            align = i != 0

            if key in parts:
                output.append(func(align))

        return ' '.join(output)

    def __len__(self):
        return len(self.blocks)


class Directory(Inode):
    __slots__ = ("dirname", "entries")

    def __init__(self, dirname: str, inode_number: int, dotdot_inode: int, owner: str = 'root', group: str = 'root'):
        super().__init__(inode_number, file_type=1, size=40, owner=owner, group=group)
        self.dirname = dirname
        self.entries: dict[str, int] = {}
        self.add(".", inode_number)
        self.add("..", dotdot_inode)

    def add(self, filename: str, inode_number: int):
        """Add a file or a dir"""
        if filename not in self.entries.keys():
            self.entries[filename] = inode_number

    def remove(self, filename: str):
        """Remove a file or a dir"""
        if filename in self.entries.keys():
            self.entries.pop(filename)

    def remove_by_inode(self, inode_number: int):
        """Remove entry by inode number"""
        for name, inode in self.entries.items():
            if inode == inode_number:
                self.entries.pop(name)
                return

    def get_inode(self, filename: str) -> int | None:
        """Return inode number if exists"""
        if filename in self.entries.keys():
            return self.entries[filename]

    def list_filenames(self) -> set[str]:
        return set(self.entries.keys())


class CommandTypes(Enum):
    EXEC = 1
    CREDENTIALS = 2
    SHELL = 3
