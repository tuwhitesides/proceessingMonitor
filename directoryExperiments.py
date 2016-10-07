# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 12:20:11 2016

@author: tuwhitesides
"""

import os
from pathlib import Path
from pylab import *

def getFileCreation(directory, tag):
    for newPath in directory.glob(tag):
        return newPath.stat().st_birthtime

    return -1

class ScanProcessing(object):
    """docstring for ScanProcessing."""
    def __init__(self, pathToScanDirectory):
        self.scanTime = getFileCreation(pathToScanDirectory, '*line.rxp')

        self.startTime = getFileCreation(pathToScanDirectory, 'processing-info.txt')

        self.coregistrationTime = getFileCreation(pathToScanDirectory, '*zChange*.jpg') - getFileCreation(pathToScanDirectory, 'processing-info.txt')

        self.processFramescanTime = getFileCreation(pathToScanDirectory, '*frame.data.mat') - getFileCreation(pathToScanDirectory, '*zChange*.jpg')

        self.processLinescanTime = getFileCreation(pathToScanDirectory, '*BeachProfile*.nc') - getFileCreation(pathToScanDirectory, '*frame.data.mat*')

        self.initialProcessingTime = self.coregistrationTime + self.processLinescanTime + self.processFramescanTime

        self.runupLag = getFileCreation(pathToScanDirectory, 'QAQC.txt') - getFileCreation(pathToScanDirectory, '*BeachProfile*.nc')

        for lineScienceMatFile in pathToScanDirectory.glob('*line.science.mat'):
            endReprocessLinescan = lineScienceMatFile.stat().st_mtime
        self.reprocessLinescanTime = endReprocessLinescan - getFileCreation(pathToScanDirectory, 'QAQC.txt')

        self.totalProcessingTime = self.initialProcessingTime + self.reprocessLinescanTime

        if self.startTime == -1:
            self.completionStatus = 0   # did not being processing
        elif self.coregistrationTime < 0:
            self.completionStatus = 1   # did not finish Coreg
        elif self.processFramescanTime < 0:
            self.completionStatus = 2   # did not finish ProcessFramescan
        elif self.processLinescanTime < 0:
            self.completionStatus = 3   # did not finish ProcessLinescan
        elif self.runupLag < 0:
            self.completionStatus = 4   # did not get RunupTooled
        elif endReprocessLinescan < getFileCreation(pathToScanDirectory, '*BeachProfile*.nc'):
            self.completionStatus = 5   # did not finish ReprocessLinescan
        else:
            self.completionStatus = 6   # finished

        self.lineRXPsize = 0
        for lineRXPFile in pathToScanDirectory.glob('*line*.rxp'):
            self.lineRXPsize += lineRXPFile.stat().st_size

        self.frameRXPsize, numFrameRXPs = 0,0
        for frameRXPFile in pathToScanDirectory.glob('*frame*.rxp'):
            self.frameRXPsize += frameRXPFile.stat().st_size
            numFrameRXPs += 1

        if self.frameRXPsize > 0:
            self.frameRXPsize = self.frameRXPsize / numFrameRXPs


if __name__ == '__main__':

    NUM_STATUSES = 7;
    allScansPath = Path('/Users/tuwhitesides/Desktop/Graduate School/Runup Reserach/rawDataFolder');

    allScansDict = {};
    for i in range(NUM_STATUSES):
        allScansDict[i] = {};

    for scanDirectory in allScansPath.iterdir():
        if scanDirectory.name[0] != '.':
            scanStats = ScanProcessing(scanDirectory);
            allScansDict[scanStats.completionStatus][scanStats.scanTime] = scanStats;

    numWithSatusIdx = list(len(allScansDict[i]) for i in range(NUM_STATUSES));
    percentWithStatusIdx = list(numWithSatusIdx[i]/sum(numWithSatusIdx) for i in range(NUM_STATUSES));

    print(percentWithStatusIdx)
    ## Make Pie Chart of Progress
    # make a square figure and axes
    figure(1, figsize=(6,6))
    ax = axes([0.1, 0.1, 0.8, 0.8])

    # The slices will be ordered and plotted counter-clockwise.
    labels = 'Waiting', 'Coreg Error', 'Framescan Error', 'Linescan Error', 'Waiting for QAQC', 'Reprocessing Error', 'Complete'

    pie(percentWithStatusIdx, labels=labels,
                    autopct='%1.1f%%', shadow=True, startangle=90)
                    # The default startangle is 0, which would start
                    # the Frogs slice on the x-axis.  With startangle=90,
                    # everything is rotated counter-clockwise by 90 degrees,
                    # so the plotting starts on the positive y-axis.

    title('Completion Status for Workflow', bbox={'facecolor':'0.8', 'pad':5})

    show()
    # Look for the last modified in all of these directories

    # calculate what I need to display
    # write those values to a json file

    # use json file to make the web dashboard

    # Web dashboard
