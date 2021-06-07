# Authour: Osama Kashif

import disktools

class Metadata():

    def __init__(self,  occupied = 0, mode = 0, uid = 0, gid = 0, nlinks = 0, size =0, ctime = 0, mtime = 0, atime = 0, location = 0, name = "", excess = 0) -> None:
        # MODE # 2 bytes
        # # UID # 2 bytes
        # # GID # 2 bytes
        # # NLINKS # 1 byte
        # # SIZE # 2 bytes, size of file in bytes
        # # CTIME # 4 bytes
        # # MTIME # 4 bytes
        # # ATIME # 4 bytes
        # # LOCATION # up to you how you do this # done as 1 byte
        # # NAME # can be here or elsewhere, 16 byte length allowed
        # # EXCESS # the remaining bytes # 27 bytes

        
        self.occupied = occupied
        self.mode = mode
        self.uid = uid
        self.gid = gid
        self.nlinks = nlinks
        self.size = size
        self.ctime = ctime
        self.mtime = mtime
        self.atime = atime
        self.location = location
        self.name = name
        self.excess = excess

    def getMetaByteArray(self) -> bytearray:
        return disktools.int_to_bytes(self.occupied,1)+disktools.int_to_bytes(self.mode,2)+disktools.int_to_bytes(self.uid,2)+disktools.int_to_bytes(self.gid,2)+disktools.int_to_bytes(self.nlinks,1)+disktools.int_to_bytes(self.size,2)+disktools.int_to_bytes(self.ctime,4)+disktools.int_to_bytes(self.mtime,4)+disktools.int_to_bytes(self.atime,4)+disktools.int_to_bytes(self.location,1)+(self.name.encode().ljust(16, b"\x00"))+disktools.int_to_bytes(self.excess,25)

    def writeMetadata(self,block_num) -> None:
        disktools.write_block(block_num, self.getMetaByteArray())

    def readMetadata(self,block_num) -> None:
        byte_arr = disktools.read_block(block_num)
        self.occupied = disktools.bytes_to_int(byte_arr[slice(0,1)])
        self.mode = disktools.bytes_to_int(byte_arr[slice(1,3)])
        self.uid = disktools.bytes_to_int(byte_arr[slice(3,5)])
        self.gid = disktools.bytes_to_int(byte_arr[slice(5,7)])
        self.nlinks = disktools.bytes_to_int(byte_arr[slice(7,8)])
        self.size = disktools.bytes_to_int(byte_arr[slice(8,10)])
        self.ctime = disktools.bytes_to_int(byte_arr[slice(10,14)])
        self.mtime = disktools.bytes_to_int(byte_arr[slice(14,18)])
        self.atime = disktools.bytes_to_int(byte_arr[slice(18,22)])
        self.location = disktools.bytes_to_int(byte_arr[slice(22,23)])
        self.name = byte_arr[slice(23,39)].decode()
        self.excess = disktools.bytes_to_int(byte_arr[slice(39,64)])