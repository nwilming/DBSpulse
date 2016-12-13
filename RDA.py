"""
Script thar receives data from EEG and looks for triggers in an EMG channel.

Communication with EEG is based on an example script from manufacturer.

Also contains a set of classes that fake an EEG on the other end to allow
debugging.
"""

# needs socket and struct library
from socket import *
from struct import *
import numpy as np
import time
from collections import deque

from sys import getsizeof as sizeof

import configure

class Marker:
    '''
    Marker class - helper class for comm. with EEG.
    '''
    def __init__(self):
        self.position = 0
        self.points = 0
        self.channel = -1
        self.type = ""
        self.description = ""

def RecvData(socket, requestedSize):
    '''
    Receives a whole message from EEG.
    Input:
        socket - socket to use for comm. with EEG
        requestedSize - how many bytes to read
    '''
    returnStream = ''
    while len(returnStream) < requestedSize:
        databytes = socket.recv(requestedSize - len(returnStream))
        if databytes == '':
            raise RuntimeError, "connection broken"
        returnStream += databytes

    return returnStream

# Helper function for faking whole messages
class RecvFake(object):
    '''
    Helper class for faking a EEG message. Limited to one channel and no markers.
    Needs to be class bcs. the EEG stream interleaves header and message packets.

    Will generate a spike in a specified interval.
    '''

    def __init__(self, Hz):
        '''
        Hz: Spike frequency
        '''
        self.startp = time.time()
        self.id = False
        self.msg = ''
        self.start = True
        self.Hz = float(Hz)

    def trigger(self):
        '''
        Return value of EMG channel
        '''
        interval = 1./self.Hz
        tp = time.time()
        if (tp-self.startp)>interval:
            self.startp = tp
            return 100.
        else:
            return np.random.randn()

    def __call__(self, socket, requestedSize):
        '''
        Return next message
        '''
        id1 = id2 = id3 = id4 = 0
        if self.start:
            # Send meta info for single channel messages
            self.msg = pack('<Ld', 1, 1000)
            self.msg += pack('<d', 100)
            self.msg += 'test\x00'
            self.id = False
            self.start = False
            properties = pack('<llllLL', id1, id2, id3, id4, sizeof(self.msg), 1)
            return properties

        if self.id:
            # This returns the header for a message and constructs the message
            # for this header
            payload = self.trigger()
            self.msg = pack('<LLL', 1, 1, 0)# Construct a valid message
            self.msg += pack('<f', payload)
            self.id = False
            hdr = pack('<llllLL', id1, id2, id3, id4, sizeof(self.msg), 4)
            return hdr
        else:
            # Transmit the message
            self.id = True
            return self.msg


def SplitString(raw):
    '''
    Helper function for splitting a raw array of
    zero terminated strings (C) into an array of python strings
    '''
    stringlist = []
    s = ""
    for i in range(len(raw)):
        if raw[i] != '\x00':
            s = s + raw[i]
        else:
            stringlist.append(s)
            s = ""

    return stringlist


def GetProperties(rawdata):
    '''
    Helper function for extracting eeg properties from a raw data array
    read from tcpip socket
    '''
    # Extract numerical data
    (channelCount, samplingInterval) = unpack('<Ld', rawdata[:12])

    # Extract resolutions
    resolutions = []
    for c in range(channelCount):
        index = 12 + c * 8
        restuple = unpack('<d', rawdata[index:index+8])
        resolutions.append(restuple[0])

    # Extract channel names
    channelNames = SplitString(rawdata[12 + 8 * channelCount:])

    return (channelCount, samplingInterval, resolutions, channelNames)


def GetData(rawdata, channelCount):
    '''
    Helper function for extracting eeg and marker data from a raw data array
    read from tcpip socket
    '''
    # Extract numerical data
    (block, points, markerCount) = unpack('<LLL', rawdata[:12])

    # Extract eeg data as array of floats
    data = []
    for i in range(points * channelCount):
        index = 12 + 4 * i
        value = unpack('<f', rawdata[index:index+4])
        data.append(value[0])

    # Extract markers
    markers = []
    index = 12 + 4 * points * channelCount
    for m in range(markerCount):
        markersize = unpack('<L', rawdata[index:index+4])

        ma = Marker()
        (ma.position, ma.points, ma.channel) = unpack('<LLl', rawdata[index+4:index+16])
        typedesc = SplitString(rawdata[index+16:index+markersize[0]])
        ma.type = typedesc[0]
        ma.description = typedesc[1]

        markers.append(ma)
        index = index + markersize[0]

    return (block, points, markerCount, data, markers)



def detect_spike(data, stds_away=2.5):
    '''
    Primitive spike detection by variable threshold crossing.
    '''
    data = np.array(data)
    #mean = np.mean(data[:-1])
    d =  np.max(data)
    if d >4500:
        print "detect", d
        return True
    return False


class EEGTrigger(object):
    '''
    Class that reads values from EEG system and runs a simple trigger detection
    algorithm. Should be used with a context manager - otherwise socket needs to
    be closed manually.
    '''
    def __init__(self, ip=configure.eeg_source_ip, port=51244, fake=False):
        self.ip = ip
        self.port = port
        self.fake = fake
        self.datadeck = deque(maxlen = 200)
        self.framecnt = 0
        self.t_start = None

    def __enter__(self):
        if not self.fake:

            self.con = socket(AF_INET, SOCK_STREAM)
            self.con.connect((self.ip, self.port))
            self.receivefunc = RecvData
        else:
            # self.fake encodes IPI
            self.receivefunc = RecvFake(1./self.fake)
            self.con = None

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.con is not None:
            self.con.close()

    def trigger(self):
        '''
        Reads all available data from EMG system and runs trigger detection on
        last second of data.
        '''
        if self.t_start is None:
            self.t_start = time.time()
        # block counter to check overflows of tcpip buffer
        lastBlock = -1
        RecvData = self.receivefunc
        # Get message header as raw array of chars
        rawhdr = RecvData(self.con, 24)
        # Split array into usefull information id1 to id4 are constants
        (id1, id2, id3, id4, msgsize, msgtype) = unpack('<llllLL', rawhdr)
        # Get data part of message, which is of variable size
        rawdata = RecvData(self.con, msgsize - 24)
        self.framecnt+=1
        if np.mod(self.framecnt, 100000)==0:
            try:
                print "FPS:", self.framecnt/(time.time()-self.t_start)
            except ZeroDivisionError:
                pass
        # Perform action dependend on the message type
        if msgtype == 1:
            # Start message, extract eeg properties and display them
            (self.channelCount, self.samplingInterval, self.resolutions, self.channelNames) = GetProperties(rawdata)
            # reset block counter
            lastBlock = -1

        elif msgtype == 4:
            # Data message, extract data and markers
            (block, points, markerCount, data, markers) = GetData(rawdata, self.channelCount)
            # Check for overflow
            if lastBlock != -1 and block > lastBlock + 1:
                print "*** Overflow with " + str(block - lastBlock) + " datablocks ***"
            lastBlock = block
            # Put data at the end of actual buffer
            #self.datadeck.extend(data)
            return detect_spike(data)

        elif msgtype == 3:
            raise RuntimeError('EMG recording stopped')
        return 0
