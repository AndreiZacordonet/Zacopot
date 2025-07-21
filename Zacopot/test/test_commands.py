import time

from core.command_parser import command_parser
from core.filesystem import FileSystem
from utils.constants import FS_SOURCE_PATH
from utils.loader import fs_loader


def test_ls_command(filesystem: FileSystem):
    assert command_parser(filesystem, 'ls') == 'bin\tetc\thome\treadme.md'
    print('Test 1 passed ✅')

    assert command_parser(filesystem, 'ls readme.md') == 'readme.md'
    print('Test 2 passed ✅')

    assert command_parser(filesystem, 'ls bin') == 'cat\tls'
    print('Test 3 passed ✅')

    assert command_parser(filesystem, 'ls /bin') == 'cat\tls'
    print('Test 4 passed ✅')

    assert command_parser(filesystem, 'ls .') == 'bin\tetc\thome\treadme.md'
    print('Test 5 passed ✅')

    assert command_parser(filesystem, 'ls .') == 'bin\tetc\thome\treadme.md'
    print('Test 6 passed ✅')

    assert command_parser(filesystem, 'ls /bin/cat') == "/bin/cat"
    print('Test 7 passed ✅')

    assert command_parser(filesystem, 'ls /bin/cat/ceva') == "ls: cannot access '/bin/cat/ceva': No such file or directory"
    print('Test 8 passed ✅')


def test_rm_command(filesystem: FileSystem):

    assert command_parser(filesystem, 'rm bibi') == "rm: 'bibi': No such file or directory"
    print('Test 1 passed ✅')

    assert command_parser(filesystem, 'rm bin') == "rm: bin: Is a directory"
    print('Test 2 passed ✅')

    assert command_parser(filesystem, 'rm readme.md') == ""
    assert command_parser(filesystem, 'ls') == 'bin\tetc\thome'
    print('Test 3 passed ✅')

    assert command_parser(filesystem, 'rm readme.md') == "rm: 'readme.md': No such file or directory"
    print('Test 4 passed ✅')

    assert command_parser(filesystem, 'rm -r bin') == ''
    assert command_parser(filesystem, 'ls') == 'etc\thome'
    print('Test 5 passed ✅')

    assert command_parser(filesystem, 'rm -r bin') == "rm: 'bin': No such file or directory"
    print('Test 6 passed ✅')


def test_mkdir_command(filesystem: FileSystem):

    assert command_parser(filesystem, 'mkdir bin') == "mkdir: cannot create directory 'bin': File exists"
    print('Test 1 passed ✅')

    assert command_parser(filesystem, 'mkdir bin2') == ""
    assert command_parser(filesystem, 'ls') == 'bin\tbin2\tetc\thome\treadme.md'
    print('Test 2 passed ✅')

    assert command_parser(filesystem, 'mkdir bin/new_folder') == ""
    print('Test 3 passed ✅')


def test_cat_command(filesystem: FileSystem):

    assert command_parser(filesystem, 'cat readme.md') == 'damn son...\r\nbig mistake over there...'
    print('Test 1 passed ✅')

    assert command_parser(filesystem, 'cat bin') == 'cat: bin: Is a directory'
    print('Test 2 passed ✅')

    assert command_parser(filesystem, 'cat readme.md bin/cat') == 'damn son...\r\nbig mistake over there...\r\nnamălețfai'
    print('Test 3 passed ✅')

    assert command_parser(filesystem, 'cat been') == "cat: 'been': No such file or directory"
    print('Test 4 passed ✅')


def test_cd_command(filesystem: FileSystem):

    assert command_parser(filesystem, 'cd bin') == ''
    assert command_parser(filesystem, 'pwd') == '/bin/'
    print('Test 1 passed ✅')

    assert command_parser(filesystem, 'cd .') == ''
    assert command_parser(filesystem, 'pwd') == '/bin/'
    print('Test 2 passed ✅')

    assert command_parser(filesystem, 'cd ..') == ''
    assert command_parser(filesystem, 'pwd') == '/'
    print('Test 3 passed ✅')

    assert command_parser(filesystem, 'cd ../home/user') == ''
    assert command_parser(filesystem, 'pwd') == '/home/user/'
    print('Test 4 passed ✅')

    assert command_parser(filesystem, 'cd ../../bin/ls') == 'bash: cd: ../../bin/ls: not a directory'
    print('Test 5 passed ✅')


def test_touch_command(filesystem: FileSystem):

    assert command_parser(filesystem, 'touch readme.md2') == ''
    assert command_parser(filesystem, 'ls') == 'bin\tetc\thome\treadme.md\treadme.md2'
    print('Test 1 passed ✅')

    assert command_parser(filesystem, 'touch bin/readme.md2') == ''
    assert command_parser(filesystem, 'ls bin') == 'cat\tls\treadme.md2'
    print('Test 2 passed ✅')

    init_time = repr(command_parser(filesystem, 'ls -l readme.md2'))
    time.sleep(60)
    assert command_parser(filesystem, 'touch readme.md2') == ''
    sec_time = repr(command_parser(filesystem, 'ls -l readme.md2'))
    assert [int(s) - int(i) for i, s in [(i, s) for i, s in zip(init_time, sec_time) if i != s]] == [1]
    print('Test 3 passed ✅')


def test_max_inodes(filesystem: FileSystem, no_inodes: int = 100):
    for i in range(no_inodes):
        command_parser(filesystem, f'touch {i}th.file')


def delete_files(filesystem: FileSystem, no_inodes: int = 100):
    for i in range(no_inodes):
        command_parser(filesystem, f'rm {i}th.file')


if __name__ == '__main__':

    file_system = FileSystem()
    fs_loader(file_system, FS_SOURCE_PATH)

    # print("\n---- Test 'ls' command ----")
    # test_ls_command(file_system)

    # print("\n---- Test 'rm' command ----")
    # test_rm_command(file_system)

    # print("\n---- Test 'mkdir' command ----")
    # test_mkdir_command(file_system)

    # print("\n---- Test 'cat' command ----")
    # test_cat_command(file_system)

    # print("\n---- Test 'cd' command ----")
    # test_cd_command(file_system)

    print("\n---- Test 'touch' command ----")
    test_touch_command(file_system)

    # start = time.time()
    # test_max_inodes(file_system, 100)
    # end = time.time()
    # # delete_files(file_system, 100)
    # print(f'creating 100 files took {end - start} seconds')
    # print(command_parser(file_system, 'ls'))

    # start = time.time()
    # test_max_inodes(file_system, 1000)
    # end = time.time()
    # delete_files(file_system, 10000)
    # print(f'creating 1000 files took {end - start} seconds')
