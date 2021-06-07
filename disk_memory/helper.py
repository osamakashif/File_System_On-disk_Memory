# Authour: Osama Kashif

import disktools
import metadata
import filedata
import free
import os

def getMode(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(1,3)])

def getUID(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(3,5)])

def getGID(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(5,7)])

def getNLinks(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(7,8)])

def getSize(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(8,10)])

def getCtime(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(10,14)])

def getMtime(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(14,18)])

def getAtime(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(18,22)])

def getLoc(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(22,23)])

def readName(block_num) -> str:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return met.getMetaByteArray()[slice(23,39)].strip(b"\x00").decode()

def getExc(block_num) -> int:
    met = metadata.Metadata()
    met.readMetadata(block_num)
    return disktools.bytes_to_int(met.getMetaByteArray()[slice(39,64)])

def getBlockNumFromName(name) -> int:
    for i in range(disktools.NUM_BLOCKS):
        if name == readName(i):
            return i
    return None

def updateNLink(block_num, new_nlink) -> None:
    metObj = metadata.Metadata()
    metObj.readMetadata(block_num)
    met = metObj.getMetaByteArray()
    met[slice(7,8)] = disktools.int_to_bytes(new_nlink,1)
    disktools.write_block(block_num, met)
    
def addFilesToDir(block_num, fileNum) -> None:
    metObj = metadata.Metadata()
    metObj.readMetadata(block_num)
    met = metObj.getMetaByteArray()
    fileLocations = bytearray()
    for i in range(39,64):
        if ((disktools.bytes_to_int(met[slice(i,i+1)]) != 0)):
            fileLocations = fileLocations + met[slice(i,i+1)]
    
    if (disktools.int_to_bytes(fileNum,1) not in getFiles(block_num)):
        fileLocations = fileLocations + disktools.int_to_bytes(fileNum,1)
    met[slice(39,64)] = fileLocations + disktools.int_to_bytes(0,25-len(fileLocations))
    disktools.write_block(block_num, met)

def remFilesFromDir(block_num, fileNum) -> None:
    metObj = metadata.Metadata()
    metObj.readMetadata(block_num)
    met = metObj.getMetaByteArray()
    fileLocations = bytearray()
    for i in range(39,64):
        if ((disktools.bytes_to_int(met[slice(i,i+1)]) != 0) and (disktools.bytes_to_int(met[slice(i,i+1)]) != fileNum)):
            fileLocations = fileLocations + met[slice(i,i+1)]
    met[slice(39,64)] = fileLocations + disktools.int_to_bytes(0,25-len(fileLocations))
    disktools.write_block(block_num, met)

def getNameFromPath(path) -> str:
    filename = ''
    if (path == '/'):
        filename = path
    else:
        filename = os.path.basename(path)
    return filename

def addFileLocation(block_num, loc) -> None:
    metObj = metadata.Metadata()
    metObj.readMetadata(block_num)
    met = metObj.getMetaByteArray()
    met[slice(22,23)] = disktools.int_to_bytes(loc,1)
    disktools.write_block(block_num, met)

def updateSize(block_num, size) -> None:
    metObj = metadata.Metadata()
    metObj.readMetadata(block_num)
    met = metObj.getMetaByteArray()
    met[slice(8,10)] = disktools.int_to_bytes(size,2)
    disktools.write_block(block_num, met)

def getFiles(block_num) -> list:
    files = []
    metObj = metadata.Metadata()
    metObj.readMetadata(block_num)
    met = metObj.getMetaByteArray()
    fileLocations = bytearray()
    for i in range(39,64):
        if (disktools.bytes_to_int(met[slice(i,i+1)]) != 0):
            files.append(readName(disktools.bytes_to_int(met[slice(i,i+1)])))

    return files

def getNextDataLocation(block_num) -> int:
    fileData = filedata.Filedata()
    fileData.readFiledata(block_num)
    return disktools.bytes_to_int(fileData.getFileByteArray()[slice(1,2)])

def getFileData(block_num) -> int:
    fileData = filedata.Filedata()
    fileData.readFiledata(block_num)
    return fileData.getFileByteArray()[slice(2,64)].decode()

def readFile(block_num) -> str:
    data = ''
    block = getLoc(block_num)
    while ((getNextDataLocation(block) != 0) and (block != 0)):
        data = data+getFileData(block).strip("\x00")
        block = getNextDataLocation(block)
    if (block != 0 ):
        data = data+getFileData(block).strip("\x00")

    return data

def clearBlock(block_num) -> None:
    disktools.write_block(block_num, disktools.int_to_bytes(0,64))

def deleteFile(block_num) -> None:
    block = getLoc(block_num)
    while ((getNextDataLocation(block) != 0) and (block != 0)):
        toClear = block
        block = getNextDataLocation(block)
        clearBlock(toClear)
    if (block != 0):
        clearBlock(block)
    clearBlock(block_num)

def checkEmptyDir(block_num) -> bool:
    if (len(getFiles(block_num)) == 0):
        return True
    else:
        return False

def deleteDir(block_num) -> None:
    clearBlock(block_num)

def writeData(block_num, data) -> None:
    length = len(data)
    if (length <= (free.getNumFree()*62)):
        blocks = 1
        if ((length%62)==0):
            blocks = length/62
        else:
            blocks = int(length/62)+1
        
        for i in range(blocks):
            loc = free.getNextFree()
            nextLoc = free.getSecondNextFree()
            extraction = ''
            if (((i*62)+62) > length):
                extraction = data[(i*62):length]
            else:
                extraction = data[(i*62):((i*62)+62)]
            
            if (i == 0) :
                addFileLocation(block_num, loc)
                if (i == (blocks -1)):
                    fileD = filedata.Filedata(1,0,extraction)
                    fileD.writeFiledata(loc)
                else:
                    fileD = filedata.Filedata(1,nextLoc,extraction)
                    fileD.writeFiledata(loc)
            else:
                if (i == (blocks -1)):
                    fileD = filedata.Filedata(1,0,extraction)
                    fileD.writeFiledata(loc)
                else:
                    fileD = filedata.Filedata(1,nextLoc,extraction)
                    fileD.writeFiledata(loc)



    else:
        print("Not enough space on disk. (File is present though.)")
        raise Exception("Not enough space on disk. (File is present though.)")