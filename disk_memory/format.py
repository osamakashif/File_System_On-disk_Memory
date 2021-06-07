# Authour: Osama Kashif

import disktools
import metadata
import free
import os
from time import time
from stat import S_IFDIR, S_IFLNK, S_IFREG

def format() -> None:
    root = metadata.Metadata(1,(S_IFDIR | 0o755),os.getuid(),os.getgid(),2,4096,int(time()),int(time()),int(time()),0,'/',0)
    disktools.low_level_format()
    root.writeMetadata(0)

if __name__ == '__main__':
    if (free.checkBlank()) :
        format()
    else:
        answer = input("There is already data on the disk. Are you sure you want to format? (y/n) [y is yes, n is no] ")
        if (answer == 'y'):
            format()
    
    for i in range(16):
        disktools.print_block(i)
    