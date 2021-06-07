#!/usr/bin/env python

# Authour: Osama Kashif

from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
# Added
from os import getuid, getgid
import os
import ntpath
import metadata
import disktools
import free
from helper import readName, getAtime, getCtime, getExc, getGID, getLoc, getMode, getMtime, getNLinks, getUID, getBlockNumFromName, updateNLink, addFilesToDir, getNameFromPath, updateSize, writeData, getFiles, readFile, deleteFile, getSize, checkEmptyDir, deleteDir, remFilesFromDir
# Added end

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str


class Small(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self):
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(
            st_mode=(S_IFDIR | 0o755),
            st_ctime=now,
            st_mtime=now,
            st_atime=now,
            st_nlink=2)


    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid
        
        filename = getNameFromPath(path)
        fileNum = getBlockNumFromName(filename)

    def create(self, path, mode):

        if (free.freeBlock()):
            self.files[path] = dict(
                st_mode=(S_IFREG | mode),
                st_nlink=1,
                st_size=0,
                st_ctime=time(),
                st_mtime=time(),
                st_atime=time())

            
            self.files[path]['st_uid'] = getuid()
            self.files[path]['st_gid'] = getgid()

            fileNum = free.getNextFree()
            whichDir = path.count('/')
            if (whichDir == 1):
                dirname = '/'
            else:
                arr = path.split('/')
                extractedName = arr[len(arr)-2]
                dirname = extractedName
            dirNum = getBlockNumFromName(dirname)
            addFilesToDir(dirNum, fileNum)
            filename = getNameFromPath(path)
            
            met = metadata.Metadata(1, self.files[path]['st_mode'],self.files[path]['st_uid'],self.files[path]['st_gid'],self.files[path]['st_nlink'], self.files[path]['st_size'], int(self.files[path]['st_ctime']), int(self.files[path]['st_mtime']), int(self.files[path]['st_atime']),0,filename,0)
            met.writeMetadata(fileNum)

        else:
            print("No more space left on disk")
            raise Exception("No more space left on disk")

        

        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        fileNum = None
        filename = getNameFromPath(path)
        fileNum = getBlockNumFromName(filename)
        whichDir = path.count('/')
        if (whichDir == 1):
            filename = getNameFromPath(path)
            fileNum = getBlockNumFromName(filename)
        else:
            arr = path.split('/')
            extractedName = arr[len(arr)-1]
            filename = extractedName
            filename = getNameFromPath(path)
            fileNum = getBlockNumFromName(filename)

        if (fileNum != None):
            self.files[path]['st_mode'] = getMode(fileNum)
            self.files[path]['st_ctime'] = getCtime(fileNum)
            self.files[path]['st_mtime'] = getMtime(fileNum)
            self.files[path]['st_atime'] = getAtime(fileNum)
            self.files[path]['st_nlink'] = getNLinks(fileNum)

        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def mkdir(self, path, mode):

        if (free.freeBlock()):
            self.files[path] = dict(
                st_mode=(S_IFDIR | mode),
                st_nlink=2,
                st_size=0,
                st_ctime=time(),
                st_mtime=time(),
                st_atime=time())
            
            self.files[path]['st_uid'] = getuid()
            self.files[path]['st_gid'] = getgid()
            
            dirname = '/'
            pathName = '/'
            fileNum = free.getNextFree()
            whichDir = path.count('/')
            if (whichDir == 1):
                dirname = '/'
            else:
                arr = path.split('/')
                extractedName = arr[len(arr)-2]
                pathName = ''
                for i in range(len(arr)-1):
                    pathName = '/'+arr[i]
                dirname = pathName
            dirNum = getBlockNumFromName(dirname)
            addFilesToDir(dirNum, fileNum)
            filename = getNameFromPath(path)

            self.files[pathName]['st_nlink'] += 1

            met = metadata.Metadata(1, self.files[path]['st_mode'],self.files[path]['st_uid'],self.files[path]['st_gid'],self.files[path]['st_nlink'], self.files[path]['st_size'], int(self.files[path]['st_ctime']), int(self.files[path]['st_mtime']), int(self.files[path]['st_atime']),0,filename,0)
            met.writeMetadata(fileNum)

            updateNLink(getBlockNumFromName(dirname), self.files[pathName]['st_nlink']) # nlink++ in disk for parent directory

        else:
            print("No more space left on disk")
            raise Exception("No more space left on disk")

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        filename = getNameFromPath(path)
        fileNum = getBlockNumFromName(filename)
        dataFromFile = readFile(fileNum)
        self.data[path] = bytes(dataFromFile.encode('ascii'))
        return self.data[path][offset:offset + size]

    def readdir(self, path, fh):
        filename = getNameFromPath(path)

        if (filename == '/'):
            filename = '/'
        else:
            arr = path.split('/')
            extractedName = arr[len(arr)-1]
            filename = extractedName
        fileNum = getBlockNumFromName(filename)

        self.files[path]['st_uid'] = getUID(fileNum)
        self.files[path]['st_gid'] = getGID(fileNum)
        
        files = getFiles(fileNum)
        for x in files:
            xNum = getBlockNumFromName(x)
            if (filename == '/'):
                x = path+x
            else:
                x = path + '/' + x
            self.files[x] = dict()
            self.files[x]['st_mode'] = getMode(xNum)
            self.files[x]['st_ctime'] = getCtime(xNum)
            self.files[x]['st_mtime'] = getMtime(xNum)
            self.files[x]['st_atime'] = getAtime(xNum)
            self.files[x]['st_nlink'] = getNLinks(xNum)
            self.files[x]['st_size'] = getSize(xNum)
            self.files[x]['st_uid'] = getUID(xNum)
            self.files[x]['st_gid'] = getGID(xNum)
        return ['.', '..'] + [x[0:] for x in files if x != '/']


    def readlink(self, path):
        return self.data[path]

    def rename(self, old, new):
        self.data[new] = self.data.pop(old)
        self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        parentName = '/'
        filename = getNameFromPath(path)
        if (filename == '/'):
            filename = '/'
        else:
            whichDir = path.count('/')
            if (whichDir == 1):
                parentName = '/'
            else:
                arr = path.split('/')
                extractedName = arr[len(arr)-1]
                parentName = arr[len(arr)-2]
                filename = extractedName
        fileNum = getBlockNumFromName(filename)
        if (filename != '/'):
            self.files.pop(path)
            self.files[parentName]['st_nlink'] -= 1
            updateNLink(getBlockNumFromName(parentName), self.files[parentName]['st_nlink']) # nlink-- in disk for parent directory
            fileNum = getBlockNumFromName(filename)
            if (checkEmptyDir(fileNum)):
                deleteDir(fileNum)
                remFilesFromDir(getBlockNumFromName(parentName), fileNum)
            else:
                raise ENOTEMPTY

    def symlink(self, target, source):
        self.files[target] = dict(
            st_mode=(S_IFLNK | 0o777),
            st_nlink=1,
            st_size=len(source))

        self.data[target] = source

    def truncate(self, path, length, fh=None):
        self.data[path] = self.data[path][:length].ljust(
            length, '\x00'.encode('ascii'))
        self.files[path]['st_size'] = length

    def unlink(self, path):
        filename = getNameFromPath(path)
        if (filename != '/'):
            parentName = '/'
            whichDir = path.count('/')
            if (whichDir == 1):
                parentName = '/'
            else:
                arr = path.split('/')
                parentName = arr[len(arr)-2]
            if path in self.data.keys():
                self.data.pop(path)
            self.files.pop(path)
            fileNum = getBlockNumFromName(filename)
            deleteFile(fileNum)
            remFilesFromDir(getBlockNumFromName(parentName), fileNum)

    def utimens(self, path, times=None):
        filename = getNameFromPath(path)
        fileNum = getBlockNumFromName(filename)

        if (fileNum != None):
            self.files[path]['st_atime'] = getAtime(fileNum)
            self.files[path]['st_mtime'] = getMtime(fileNum)

    def write(self, path, data, offset, fh):
        self.data[path] = (
            # make sure the data gets inserted at the right offset
            self.data[path][:offset].ljust(offset, '\x00'.encode('ascii'))
            + data
            # and only overwrites the bytes that data is replacing
            + self.data[path][offset + len(data):])
        self.files[path]['st_size'] = len(self.data[path])
        filename = getNameFromPath(path)
        fileNum = getBlockNumFromName(filename)
        writeData(fileNum, self.data[path])
        updateSize(fileNum,self.files[path]['st_size'])
        return len(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Small(), args.mount, foreground=True)
