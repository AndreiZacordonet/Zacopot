
BLOCK_SIZE = 4096   # bytes

DISK_FILE_NAME = 'disk_file.bin'
KEY_PATH = 'secrets/server.key'
FS_SOURCE_PATH = 'fs_source_dir'
LOG_DIR = 'logs'

BANNER = b'Welcome to the research data center for the Ukraine Conservation Biology Team!\r\n' + 'Ласкаво просимо до каталогу даних дослідницької групи з охорони біорізноманіття!\r\n'.encode()
DISTRO = 'debian'

MAX_CONNECTIONS = 20
MAX_BUFFER_SIZE = 4096

# superblock options
TOTAL_BLOCKS = 1000
TOTAL_INODES = 200
