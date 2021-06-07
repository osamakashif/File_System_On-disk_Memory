# Authour: Osama Kashif

import disktools

def checkBlank() -> bool:
    for i in range(16):
        if (disktools.bytes_to_int(disktools.read_block(i)[slice(0,1)]) == 1) :
            return False

    return True

def getFree() -> list:
    free = []
    for i in range(16):
        if (disktools.bytes_to_int(disktools.read_block(i)[slice(0,1)]) == 0) :
            free.append(i)
    return free

def freeBlock() -> bool:
    if (len(getFree()) == 0):
        return False
    else:
        return True

def getNextFree() -> int:
    return getFree()[0]

def getSecondNextFree() -> int:
    return getFree()[1]

def getNumFree() -> int:
    return len(getFree())