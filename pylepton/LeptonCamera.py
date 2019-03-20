from itertools import cycle
from pathlib import Path
import numpy as np
import sys
import os
import subprocess
import time
import datetime
from pylepton.Lepton3 import Lepton3

class LeptonCamera:
    """
    A class representation of a lepton camera object

    Attributes
    ------------
    testName : str
        a descriptive name for current test, will be used to name saved data files
    pixelLocs : dict
        a dictionary of location information for points of interests
        Format: Key - string describing location information e.g. 'first point'
                Value - a list of length 2 of row and column information; e.g. [50, 79]
    """


    def __init__(self, testName, pixelLocs):
        self.testName = testName
        self.pixelLocs = pixelLocs
        #self.dataFolder = False

    """
    Controls lepton module to capture a thermal image. Updates rawArr
    """
    def takeImg(self):
        with Lepton3("/dev/spidev0.0") as l:
            rawArray, _ = l.capture()
        self.rawArr = rawArray

    """
    Reads from file saved by takeImg and convert temperatures to a 120 by 160 array

    Return
    ------------

    a 2d numpy array of temperature information in celsius
    """
    def getTempArr(self):
        return self.rawArr / 100 - 273.15

    """
    Select a subarray centered around a specified point

    Parameters
    ------------
    squareArrSize : int
        the width of the square subarray; has to be an positive odd number larger than 1
    row : int
        center point row number
    col : int
        center point column number

    Return
    ------------
    A subarray centered around given center point
    """
    def regionalTempArr(self, extensionSize, row, col):
        # select a region of interest array from user given row, col, size value
        tempArr = self.getTempArr()
        leftSize = extensionSize # make left right up down extension size to user wanted size
        rightSize = extensionSize
        upSize = extensionSize
        downSize = extensionSize
        # check if default size is within 160 * 120 region, if not, modifity default size
        if (col - leftSize < 0):
            leftSize = col
        if (col + rightSize > 160):
            rightSize = 160 - col - 1
        if (row - upSize < 0):
            upSize = row
        if (row + downSize > 120):
            downSize = 120 - row - 1
        regionTempArr = np.empty([upSize + 1 + downSize, leftSize + 1 + rightSize])
        regionStartRow = row - upSize
        regionStartCol = col - leftSize
        for i in range(0, len(regionTempArr)):
            for j in range(0, len(regionTempArr[0])):
                regionTempArr[i, j] = tempArr[regionStartRow + i, regionStartCol + j]
        return regionTempArr

    """
    Extract temperature at a given point in celsius

    Parameters
    ------------
    row : int
        point row number
    col : int
        point column number

    Return
    ------------
    Temperature value at given point
    """
    def getPointTemp(self, row, col):
        tempArr = self.getTempArr()
        return tempArr[row][col]

    """
    Finds the maximum value in a given temperature array

    Parameters
    ------------
    tempArr : Temperature array to find max from

    Return
    ------------
    The maximum temperature in this array
    """
    @staticmethod
    def tempMax(tempArr):
        # Finds the maximum temperature in regionTempArr
        return np.amax(tempArr)

    """
    Finds the minimum value in a given temperature array

    Parameters
    ------------
    tempArr : Temperature array to find min from

    Return
    ------------
    The minimum temperature in this array
    """
    @staticmethod
    def tempMin(tempArr):
        # Finds the mimimum temperature in the area
        return np.amin(tempArr)

    """
    Finds the average value in a given temperature array

    Parameters
    ------------
    tempArr : Temperature array to find avg from

    Return
    ------------
    The average temperature in this array
    """
    @staticmethod
    def tempAvg(tempArr):
        # Finds the average temperature in the area
        return np.mean(tempArr)

    """
    Log data for current frame and writes to a folder named after testName instance variable

    Parameter
    ------------
    extensionSize : int with default value 3
        equivalent to meaning of extensionSize used in regionalTempArr(self, extensionSize, row, col)

    Output
    ------------
    A folder in current path named after testName. Inside the folder is text files of temperature information:
        1. Time and date the data was saved
        1. point temperature at each point in user specified in pixelLocs
        2. regional temperature max/min/avg in a temperature region surrounding each point with user specified squareArrSize
        3. A full temperature array
    """
    def saveData(self, extensionSize = 3):
        # create a folder named after testName and save data for current frame to a txtfile in that folder
        if not Path(self.testName).exists():
            # if dataFolder has not yet been created
            os.mkdir(self.testName)
        # find an unused name for text file
        fileNumber = 1
        dataFileName = self.testName + 'Lepton' + str(fileNumber) + '.txt'
        filePath = os.path.join(os.getcwd(), self.testName, dataFileName)
        fileExist = os.path.isfile(filePath)
        while fileExist == True:
            fileNumber = fileNumber + 1
            dataFileName = self.testName + 'Lepton' + str(fileNumber) + '.txt'
            filePath = os.path.join(os.getcwd(), self.testName, dataFileName)
            fileExist = os.path.isfile(filePath)
        filePath = os.path.join(os.getcwd(), self.testName, dataFileName)
        fo = open(filePath, 'w')
        fo.write('Extracted from file: ' + str(self.fileName) + '\n')
        dnt = datetime.datetime.now()
        fo.write('Date: ' + str(dnt.month) + '/' + str(dnt.day) + '/' + str(dnt.year) + '\n')
        fo.write('Time: ' + str(dnt.hour) + ':' + str(dnt.minute) + ':' + str(dnt.second) + '\n')
        # iterate through self.pixelLoc and write information about each location to file
        for pixelLoc in self.pixelLocs.values():
            regionalTempArr = self.regionalTempArr(extensionSize, pixelLoc[0], pixelLoc[1])
            regionMax = self.tempMax(regionalTempArr)
            regionMin = self.tempMin(regionalTempArr)
            regionAvg = self.tempAvg(regionalTempArr)
            fo.write('The temperature at row ' + str(pixelLoc[0]) + ' column ' + str(pixelLoc[1]) + ' is ' + str(self.getPointTemp(pixelLoc[0], pixelLoc[1])) + ' degree C\n')
            fo.write('The maximum temperature throughout a 3x3 area surrounding given location is' + str(regionMax) + ' degree C\n')
            fo.write('The minimum temperature throughout a 3x3 area surrounding given location is' + str(regionMin) + ' degree C\n')
            fo.write('The average temperature throughout a 3x3 area surrounding given location is' + str(regionAvg) + ' degree C\n')
            fo.write('\n')
        # writes the full temperature array to text file
        fo.write('Full temperature array:')
        currTempArr = self.getTempArr()
        for i in range(0, 120):
            for j in range(0, 160):
                if j == 0:
                    fo.write('\n')
                fo.write(str(currTempArr[i][j]) + '  ')
        # back to original working directory
        fo.close()
