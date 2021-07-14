#! /usr/bin/env python3

"""JPEG 2000 Automated Quality Assessment Tool

Automated quality control of JP2 images for KB digitisation projects
Wraps around jpylyzer
Johan van der Knijff

Requires Python 3.2 or more recent

Preconditions:

- Images that are to be analysed have a .jp2 extension (all others ignored!)
- Parent directory of master images is called 'master'
- Parent directory of access images is called 'access'
- Parent directory of target images is called 'targets-jp2'

Master, access and targets directories may be located in a subdirectory.
Other than that organisation of images may follow arbitrary directory structure
(jprofile does a recursive scan of whole directory tree of a batch)

Copyright 2013, 2017 Johan van der Knijff,
KB/National Library of the Netherlands
"""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import imp
import time
import argparse
import xml.etree.ElementTree as ET
from jpylyzer import jpylyzer
from lxml import isoschematron
from lxml import etree
from . import config

__version__ = "0.9.0"


def main_is_frozen():
    """Determine if this jprofile instance is 'frozen' executable"""
    return (hasattr(sys, "frozen") or  # new py2exe
            hasattr(sys, "importers") or  # old py2exe
            imp.is_frozen("__main__"))  # tools/freeze


def get_main_dir():
    """Return installation directory"""
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])


def errorExit(msg):
    """Write error to stderr and exit"""
    msgString = ("ERROR: " + msg + "\n")
    sys.stderr.write(msgString)
    sys.exit()


def checkFileExists(fileIn):
    """Check if file exists and exit if not"""
    if not os.path.isfile(fileIn):
        msg = fileIn + " does not exist!"
        errorExit(msg)


def checkDirExists(pathIn):
    """Check if directory exists and exit if not"""
    if not os.path.isdir(pathIn):
        msg = pathIn + " does not exist!"
        errorExit(msg)


def openFileForAppend(wFile):
    """Opens file for writing in append + binary mode"""
    try:
        # Python 3.x
        if sys.version.startswith('3'):
            f = open(wFile, "a", encoding="utf-8")
        # Python 2.x
        elif sys.version.startswith('2'):
            f = open(wFile, "a")
        return f

    except Exception:
        msg = wFile + " could not be written"
        errorExit(msg)


def removeFile(fileIn):
    """Remove a file"""
    try:
        if os.path.isfile(fileIn):
            os.remove(fileIn)
    except Exception:
        msg = "Could not remove " + fileIn
        errorExit(msg)


def constructFileName(fileIn, extOut, suffixOut):
    """Construct filename by replacing path by pathOut,
    adding suffix and extension
    """

    fileInTail = os.path.split(fileIn)[1]
    baseNameIn = os.path.splitext(fileInTail)[0]
    baseNameOut = baseNameIn + suffixOut + "." + extOut
    fileOut = baseNameOut
    return fileOut


def parseCommandLine():
    """Parse command line"""

    # Create parser
    parser = argparse.ArgumentParser(description="JP2 profiler for KB")

    # Add arguments
    parser.add_argument('batchDir',
                        action="store",
                        help="batch directory")
    parser.add_argument('prefixOut',
                        action="store",
                        help="prefix of output files")
    parser.add_argument('-p', '--profile',
                        action="store",
                        default="list",
                        help='name of profile that defines schemas for master,\
                               access and target images. Type "l" or "list" \
                              to view all available profiles')
    parser.add_argument('--version', '-v',
                        action="version",
                        version=__version__)

    # Parse arguments
    args = parser.parse_args()

    # Normalise all file paths
    args.batchDir = os.path.normpath(args.batchDir)

    return args


def listProfiles(profilesDir):
    """List all available profiles"""
    profileNames = os.listdir(profilesDir)
    print("\nAvailable profiles:\n")
    for i in range(len(profileNames)):
        print(profileNames[i])
    sys.exit()


def readProfile(profile, profilesDir, schemasDir):
    """Read a profile and return dictionary with all associated schemas"""

    profile = os.path.join(profilesDir, profile)

    # Check if profile exists and exit if not
    checkFileExists(profile)

    # Parse XML tree
    try:
        tree = ET.parse(profile)
        prof = tree.getroot()
    except Exception:
        msg = "error parsing " + profile
        errorExit(msg)

    # Locate schema elements
    schemaMasterElement = prof.find("schemaMaster")
    schemaAccessElement = prof.find("schemaAccess")
    schemaTargetRGBElement = prof.find("schemaTargetRGB")
    schemaTargetGrayElement = prof.find("schemaTargetGray")
    schemaTargetAccessRGBElement = prof.find("schemaTargetAccessRGB")
    schemaTargetAccessGrayElement = prof.find("schemaTargetAccessGray")

    # Get corresponding text values
    schemaMaster = os.path.join(schemasDir, schemaMasterElement.text)
    schemaAccess = os.path.join(schemasDir, schemaAccessElement.text)
    schemaTargetRGB = os.path.join(schemasDir, schemaTargetRGBElement.text)
    schemaTargetGray = os.path.join(schemasDir, schemaTargetGrayElement.text)
    schemaTargetAccessRGB = os.path.join(schemasDir, schemaTargetAccessRGBElement.text)
    schemaTargetAccessGray = os.path.join(schemasDir, schemaTargetAccessGrayElement.text)

    # Check if all files exist, and exit if not
    checkFileExists(schemaMaster)
    checkFileExists(schemaAccess)
    checkFileExists(schemaTargetRGB)
    checkFileExists(schemaTargetGray)
    checkFileExists(schemaTargetAccessRGB)
    checkFileExists(schemaTargetAccessGray)

    # Add schemas to a dictionary
    schemas = {"schemaMaster": schemaMaster,
               "schemaAccess": schemaAccess,
               "schemaTargetRGB": schemaTargetRGB,
               "schemaTargetGray": schemaTargetGray,
               "schemaTargetAccessRGB": schemaTargetAccessRGB,
               "schemaTargetAccessGray": schemaTargetAccessGray}

    return schemas


def readAsLXMLElt(xmlFile):
    """Parse XML file with lxml and return result as element object
    (not the same as Elementtree object!)
    """

    f = open(xmlFile, 'r')
    # Note we're using lxml.etree here rather than elementtree
    resultAsLXMLElt = etree.parse(f)
    f.close()

    return resultAsLXMLElt


def getFilesFromTree(rootDir, extensionString):
    """Walk down whole directory tree (including all subdirectories) and
    return list of those files whose extension contains user defined string
    NOTE: directory names are disabled here!!
    implementation is case insensitive (all search items converted to
    upper case internally!
    """

    extensionString = extensionString.upper()

    filesList = []

    for dirname, dirnames, filenames in os.walk(rootDir):
        # Suppress directory names
        for subdirname in dirnames:
            thisDirectory = os.path.join(dirname, subdirname)

        for filename in filenames:
            thisFile = os.path.join(dirname, filename)
            thisExtension = os.path.splitext(thisFile)[1]
            thisExtension = thisExtension.upper()
            if extensionString in thisExtension:
                filesList.append(thisFile)
    return filesList


def getPathComponentsAsList(path):
    """Returns a list that contains all path components (dir names) in path
    Adapted from:
    http://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
    """

    drive, path_and_file = os.path.splitdrive(path)
    pathComponent, fileComponent = os.path.split(path_and_file)

    folders = []
    while 1:
        pathComponent, folder = os.path.split(pathComponent)

        if folder != "":
            folders.append(folder)
        else:
            if pathComponent != "":
                folders.append(pathComponent)

            break

    folders.reverse()
    return(folders, fileComponent)

def extractSchematron(report):
    """Parse output of Schematron validation and extract interesting bits"""

    outString=""

    for elem in report.iter():
        if elem.tag == "{http://purl.oclc.org/dsdl/svrl}failed-assert":

            config.status = "fail"

            # Extract test definition
            test = elem.get('test')
            outString += 'Test "' + test + '" failed ('

            # Extract text description from text element
            for subelem in elem.iter():
                if subelem.tag == "{http://purl.oclc.org/dsdl/svrl}text":
                    description = (subelem.text)
                    outString += description + ")" + config.lineSep
    return outString


def extractJpylyzer(resultJpylyzer):
    """Parse output of Jpylyzer and extract interesting bits"""

    outString=""
    validationOutcome = resultJpylyzer.find("isValid").text

    if validationOutcome == "False":

        # Locate test elements
        # testsElt = resultJpylyzer.find("tests")

        # For some strange reason above statement returns 'None' under
        # Python 3! Workaround: find it by iterating over resultJpylyzer

        for element in resultJpylyzer.iter():
            if element.tag == "tests":
                testsElt = element

        outString += "*** Jpylyzer JP2 validation errors:" \
            + config.lineSep

        # Iterate over tests element and report names of all
        # tags thatcorrespond to tests that failed

        tests = list(testsElt.iter())

        for j in tests:
            if j.text == "False":
                outString += "Test " + j.tag + \
                    " failed" + config.lineSep
    return outString


def processJP2(JP2):
    """Process one JP2"""

    # Initialise status (pass/fail)
    config.status = "pass"
    schemaMatch = True

    # Initialise empty text string for error log output
    ptOutString = ""

    # Create list that contains all file path components (dir names)
    pathComponents, fName = getPathComponentsAsList(JP2)

    # Select schema based on value of parentDir (master/access/targets-jp2)

    if "master" in pathComponents:
        mySchema = config.schemaMasterLXMLElt
    elif "access" in pathComponents:
        mySchema = config.schemaAccessLXMLElt
    elif "targets-jp2_access" in pathComponents:
        if "_MTF_GRAY_" in fName:
            mySchema = config.schemaTargetAccessGrayLXMLElt
        else:
            mySchema = config.schemaTargetAccessRGBLXMLElt
    elif "targets-jp2" in pathComponents:
        if "_MTF_GRAY_" in fName:
            mySchema = config.schemaTargetGrayLXMLElt
        else:
            mySchema = config.schemaTargetRGBLXMLElt
    else:
        schemaMatch = False
        config.status = "fail"
        description = "Name of parent directory does not match any schema"
        ptOutString += description + config.lineSep

    if schemaMatch:

        # Run jpylyzer on image and write result to text file
        try:
            resultJpylyzer = jpylyzer.checkOneFile(JP2)
            resultAsXML = ET.tostring(resultJpylyzer, 'UTF-8', 'xml')
        except Exception:
            config.status = "fail"
            description = "Error running jpylyzer"
            ptOutString += description + config.lineSep

        try:
            # Start Schematron magic ...
            schematron = isoschematron.Schematron(mySchema,
                                                  store_report=True)

            # Reparse jpylyzer XML with lxml since using ET object
            # directly doesn't work
            resJpylyzerLXML = etree.fromstring(resultAsXML)

            # Validate jpylyzer output against schema
            schemaValidationResult = schematron.validate(resJpylyzerLXML)
            report = schematron.validation_report

        except Exception:
            config.status = "fail"
            description = "Schematron validation resulted in an error"
            ptOutString += description + config.lineSep

        # Parse output of Schematron validation and extract
        # interesting bits
        try:
            schOutString = extractSchematron(report)
            ptOutString += schOutString
        except Exception:
            config.status = "fail"
            description = "Error processing Schematron output"
            ptOutString += description + config.lineSep

        # Parse jpylyzer XML output and extract info on failed tests
        # in case image is not valid JP2
        try:
            jpOutString = extractJpylyzer(resultJpylyzer)
            ptOutString += jpOutString
        except Exception:
            config.status = "fail"
            description = "Error processing Jpylyzer output"
            ptOutString += description + config.lineSep
            raise

    if config.status == "fail":

        config.fFailed.write(JP2 + config.lineSep)
        config.fFailed.write("*** Schema validation errors:" + config.lineSep)
        config.fFailed.write(ptOutString)
        config.fFailed.write("####" + config.lineSep)

    statusLine = JP2 + "," + config.status + config.lineSep
    config.fStatus.write(statusLine)


def main():
    """Main function"""

    # Locate package directory
    packageDir = os.path.dirname(os.path.abspath(__file__))

    # Profiles and schemas dirs. Location depends on whether jprofile instance
    # is package or frozen executable (PyInstaller)

    if main_is_frozen():
        profilesDir = os.path.join(os.path.dirname(sys.executable), "profiles")
        schemasDir = os.path.join(os.path.dirname(sys.executable), "schemas")
    else:
        profilesDir = os.path.join(packageDir, "profiles")
        schemasDir = os.path.join(packageDir, "schemas")

    # Check if profiles dir exists and exit if not
    checkDirExists(profilesDir)

    # Get input from command line
    args = parseCommandLine()

    batchDir = args.batchDir
    prefixOut = args.prefixOut

    profile = args.profile
    if profile in["l", "list"]:
        listProfiles(profilesDir)

    # Get schema locations from profile
    schemas = readProfile(profile, profilesDir, schemasDir)

    schemaMaster = schemas["schemaMaster"]
    schemaAccess = schemas["schemaAccess"]
    schemaTargetRGB = schemas["schemaTargetRGB"]
    schemaTargetGray = schemas["schemaTargetGray"]
    schemaTargetAccessRGB = schemas["schemaTargetAccessRGB"]
    schemaTargetAccessGray = schemas["schemaTargetAccessGray"]

    # Get schemas as lxml.etree elements
    config.schemaMasterLXMLElt = readAsLXMLElt(schemaMaster)
    config.schemaAccessLXMLElt = readAsLXMLElt(schemaAccess)
    config.schemaTargetRGBLXMLElt = readAsLXMLElt(schemaTargetRGB)
    config.schemaTargetGrayLXMLElt = readAsLXMLElt(schemaTargetGray)
    config.schemaTargetAccessRGBLXMLElt = readAsLXMLElt(schemaTargetAccessRGB)
    config.schemaTargetAccessGrayLXMLElt = readAsLXMLElt(schemaTargetAccessGray)

    # Set line separator for output/ log files to OS default
    config.lineSep = "\n"

    # Open log files for writing (append)

    # File with summary of quality check status (pass/fail) for each image
    statusLog = os.path.normpath(prefixOut + "_status.csv")
    removeFile(statusLog)
    config.fStatus = openFileForAppend(statusLog)

    # File that contains detailed results for all images that failed
    # quality check
    failedLog = os.path.normpath(prefixOut + "_failed.txt")
    removeFile(failedLog)
    config.fFailed = openFileForAppend(failedLog)

    listJP2s = getFilesFromTree(batchDir, "jp2")

    # start clock for statistics
    start = time.time()
    print("jprofile started: " + time.asctime())

    # Iterate over all JP2s 
    for i in range(len(listJP2s)):
        myJP2 = os.path.abspath(listJP2s[i])
        processJP2(myJP2)

    end = time.time()

    # Close output files
    config.fStatus.close()
    config.fFailed.close()

    print("jprofile ended: " + time.asctime())

    # Elapsed time (seconds)
    timeElapsed = end - start
    timeInMinutes = round((timeElapsed / 60), 2)

    print("Elapsed time: " + str(timeInMinutes) + " minutes")


if __name__ == "__main__":
    main()
