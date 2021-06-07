
# Authour: Osama Kashif

# File for testing and seeing block status

import disktools
import metadata

def readName(block_num) -> None:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return met.getMetaByteArray()[slice(21,37)].strip(b"\x00").decode()

if __name__ == '__main__':
    for i in range(16):
        disktools.print_block(i)