# Authour: Osama Kashif

import disktools

class Filedata():

    def __init__(self,  occupied = 0, nextLoc = 0, data = 0) -> None:
        # Occupied # 1 byte
        # Last # 1 byte
        # Next location # 1 byte
        # Data # 62 bytes
        self.occupied = occupied
        self.nextLoc = nextLoc
        self.data = data

    def getFileByteArray(self) -> bytearray:
        return disktools.int_to_bytes(self.occupied,1)+disktools.int_to_bytes(self.nextLoc,1)+(self.data.ljust(62, b"\x00"))

    def writeFiledata(self,block_num) -> None:
        disktools.write_block(block_num, self.getFileByteArray())

    def readFiledata(self,block_num) -> None:
        byte_arr = disktools.read_block(block_num)
        self.occupied = disktools.bytes_to_int(byte_arr[slice(0,1)])
        self.nextLoc = disktools.bytes_to_int(byte_arr[slice(1,2)])
        self.data = byte_arr[slice(2,64)]