#! /usr/bin/env python
#
# JPEG 2000 Automated Quality Assessment Tool
# Automated quality control of JP2 images for KB digitisation projects.
# Wraps around jpylyzer and Probatron
# Johan van der Knijff
#
# Requires Python v. 2.7 
#
# Copyright 2013 Johan van der Knijff, KB/National Library of the Netherlands
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Preconditions:
#
# - Tool is run on a Windows-platform
# - All images that are to be analysed have a .jp2 extension (all others are ignored!)
# - Parent directory of master images is called 'master' (may be in subdirectory)
# - Parent directory of access images is called 'access' (may be in subdirectory)
# - Parent directory of target images is called 'targets-jp2' (may be in subdirectory)
#
# Other than that organisation of images may follow arbitrary directory structure
# (this tool does a recursive scan of whole directory tree of a batch)


__version__= "0.4.1"

import sys
import os
import imp
import shutil
import time
import argparse
import xml.etree.ElementTree as ET
import subprocess as sub
import jpylyzer
import config
import codecs
from lxml import isoschematron
from lxml import etree

def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze
    
def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])

def errorExit(msg):
    msgString=("ERROR: " +msg + "\n")
    sys.stderr.write(msgString)
    sys.exit()
    
def checkFileExists(fileIn):
    # Check if file exists and exit if not
    if os.path.isfile(fileIn)==False:
        msg=fileIn + " does not exist!"
        errorExit(msg)
        
def checkDirExists(pathIn):
    # Check if directory exists and exit if not
    if os.path.isdir(pathIn)==False:
        msg=pathIn + " does not exist!"
        errorExit(msg)
        
def openFileForAppend(file):
    # Opens file for writing in append + binary mode
    try:
        f=open(file,"ab")
        return(f)
    except Exception:
        msg=file + " could not be written"
        errorExit(msg)

def removeFile(file):
    try:
        if os.path.isfile(file)==True:
            os.remove(file)
    except Exception:
        msg= "Could not remove " + file
        errorExit(msg)

def constructFileName(fileIn,extOut,suffixOut):

    # Construct filename by replacing path by pathOut,
    # adding suffix and extension
    
    fileInTail=os.path.split(fileIn)[1]

    baseNameIn=os.path.splitext(fileInTail)[0]
    baseNameOut=baseNameIn + suffixOut + "." + extOut
    fileOut=baseNameOut

    return(fileOut)

def addPath(pathIn,fileIn):
    result=os.path.normpath(pathIn+ "/" + fileIn)
    return(result)
    
def parseCommandLine():
    # Create parser
    parser = argparse.ArgumentParser(description="JP2 profiler for KB",version=__version__)
    
    # Add arguments
    parser.add_argument('batchDir', action="store", help="batch directory")
    parser.add_argument('prefixOut', action="store", help="prefix of output files")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p','--profile', action="store", help="name of profile that defines schemas for master, access and target images")
    group.add_argument('-l', '--listprofiles', action="store_true")
   
    # Parse arguments
    args=parser.parse_args()
    
    # Normalise all file paths
    args.batchDir=os.path.normpath(args.batchDir)
    
    return(args)

def getConfiguration(configFile):

    # What is the location of this script?
    appPath=os.path.abspath(get_main_dir())

    # Parse XML tree
    try:
        tree = ET.parse(configFile)
        config = tree.getroot()
    except Exception:
        msg="error parsing " + configFile
        errorExit(msg)
    
    # Locate configuration elements
    javaElement=config.find("java")
    
    # Get corresponding text values
    java=os.path.normpath(javaElement.text)
    probatronApp=addPath(appPath + "/probatron/","probatron.jar")
        
    # Check if all files exist, and exit if not
    checkFileExists(java)
    checkFileExists(probatronApp)
            
    return(java,probatronApp)


def listProfiles(profilesDir):
    profileNames=os.listdir(profilesDir)
    
    for i in range(len(profileNames)):
        print(profileNames[i])
    sys.exit()
    

def readProfile(profile):
       
    # What is the location of this script?
    appPath=os.path.abspath(get_main_dir())
    
    profile=addPath(appPath + "/profiles/",profile)

    # Check if profile exists and exit if not
    checkFileExists(profile)

    # Parse XML tree
    try:
        tree = ET.parse(profile)
        prof = tree.getroot()
    except Exception:
        msg="error parsing " + profile
        errorExit(msg)
    
    # Locate schema elements
    schemaMasterElement=prof.find("schemaMaster")
    schemaAccessElement=prof.find("schemaAccess")
    schemaTargetElement=prof.find("schemaTarget")
    
    # Get corresponding text values
    schemaMaster=addPath(appPath + "/schemas/",schemaMasterElement.text)
    schemaAccess= addPath(appPath + "/schemas/",schemaAccessElement.text)
    schemaTarget= addPath(appPath + "/schemas/",schemaTargetElement.text) 
    
    # Check if all files exist, and exit if not
    checkFileExists(schemaMaster)
    checkFileExists(schemaAccess)
    checkFileExists(schemaTarget)
    
    # HACK: Probatron exits with URL Exception if schema is a  standard (full) file path,
    # this makes it work (at least under Windows)
    #schemaMaster="file:///" + schemaMaster
    #schemaAccess="file:///" +schemaAccess
    #schemaTarget="file:///" +schemaTarget
    
    return(schemaMaster,schemaAccess,schemaTarget)


def launchSubProcess(systemString):
    # Launch subprocess and return exit code, stdout and stderr
    try:
        # Execute command line; stdout + stderr redirected to objects
        # 'output' and 'errors'.
        p = sub.Popen(systemString,stdout=sub.PIPE,stderr=sub.PIPE)
        output, errors = p.communicate()
                
        # Decode to UTF8
        outputAsString=output.decode('utf-8')
        errorsAsString=errors.decode('utf-8')
                
        exitStatus=p.returncode
  
    except Exception:
        # I don't even want to start thinking how one might end up here ...
        exitStatus=-99
        outputAsString=""
        errorsAsString=""
    
    return exitStatus,outputAsString,errorsAsString

def getFilesFromTree(rootDir, extensionString):
    # Walk down whole directory tree (including all subdirectories)
    # and return list of those files whose extension contains user defined string
    # NOTE: directory names are disabled here!!
    # implementation is case insensitive (all search items converted to
    # upper case internally!

    extensionString=extensionString.upper()

    filesList=[]
    for dirname, dirnames, filenames in os.walk(rootDir):
        #Suppress directory names
        for subdirname in dirnames:
            thisDirectory=os.path.join(dirname, subdirname)

        for filename in filenames:
            thisFile=os.path.join(dirname, filename)
            thisExtension=os.path.splitext(thisFile)[1]
            thisExtension=thisExtension.upper()
            if extensionString in thisExtension:
                filesList.append(thisFile)
    return filesList

def getPathComponentsAsList(path):
    
    # Adapted from:
    # http://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
    
    drive,path_and_file=os.path.splitdrive(path)
    path,file=os.path.split(path_and_file)
    
    folders=[]
    while 1:
        path,folder=os.path.split(path)

        if folder!="":
            folders.append(folder)
        else:
            if path!="":
                folders.append(path)

            break

    folders.reverse()
    return(folders)
                    
def main():
    
    # What is the location of this script/executable
    appPath=os.path.abspath(get_main_dir())
    
    # Configuration file
    configFile=os.path.abspath(appPath + "/config.xml")
    
    # Check if config file exists, and exit if not
    checkFileExists(configFile)
    
    # Profiles dir
    profilesDir= os.path.abspath(appPath + "/profiles/")

    # Check if cprofiles dir exists and exit if not
    checkDirExists(profilesDir)

    # Get input from command line
    args=parseCommandLine()
    
    batchDir=args.batchDir
    prefixOut=args.prefixOut
    
    if args.listprofiles:
            
        listProfiles(profilesDir)
        
    else:
        profile=args.profile
        if profile == None:
            errorExit("no profile specified!") 
               
    # Get Java location from config file 
    java,probatronApp=getConfiguration(configFile)
        
    # Get schema loctions from profile
    schemaMaster,schemaAccess,schemaTarget=readProfile(profile)
    
    # Set line separator for output/ log files to OS default
    lineSep=os.linesep
  
    # Open log files for writing (append + binary mode so we don't have to worry
    # about encoding issues).
    # IMPORTANT: files are overwitten for each new session (hence 'removeFile'
    # before opening below!).
    
    # File with summary of quality check status (pass/fail) for each image
    statusLog=os.path.normpath(prefixOut + "_status.csv")
    removeFile(statusLog)
    fStatus=openFileForAppend(statusLog)
    
    # File that contains detailed results for of all images that failed quality check 
    failedLog=os.path.normpath(prefixOut + "_failed.txt")
    removeFile(failedLog)
    fFailed=openFileForAppend(failedLog)
    
    listJP2s=getFilesFromTree(batchDir, "jp2")

    # start clock for statistics
    start = time.clock()
    print("jprofile started: " + time.asctime())
    
    for i in range(len(listJP2s)):
        myJP2=os.path.abspath(listJP2s[i])
        
        # Initialise status (pass/fail)
        status="pass"
        schemaMatch=True
        
        # Initialise empty text string for error log output
        ptOutString=""
                        
        # Create list that contains all file ptath components (dir names)
        pathComponents=getPathComponentsAsList(myJP2)
                
        # Select schema based on value of parentDir (master/access/targets-jp2)
        
        if "master" in pathComponents:
            mySchema=schemaMaster
        elif "access" in pathComponents:
            mySchema=schemaAccess
        elif "targets-jp2" in pathComponents: 
            mySchema=schemaTarget

        else:
            schemaMatch=False
            status="fail"
            description="Name of parent directory does not match any schema"
            ptOutString +=description + lineSep    
        
        if schemaMatch == True:
            
            #Run jpylyzer on image and write result to text file
            try:
                resultJpylyzer=jpylyzer.checkOneFile(myJP2)
                resultAsXML = ET.tostring(resultJpylyzer, 'UTF-8', 'xml')                                
            except:
                status="fail"
                description="Error running jpylyzer"
                ptOutString +=description + lineSep
             
            try:
                f = open(mySchema, 'r')
            
                # Note we're using lxml.etree here rather than elementtree (yes, it's confusing!)
                sct_doc = etree.parse(f)
                schematron = isoschematron.Schematron(sct_doc, store_report = True)
                #schematron = isoschematron.Schematron(sct_doc)
                
                # Reparsing XML with lxml since using ET object directly doesn't work
                resultJpylyzerLXML = etree.fromstring(resultAsXML)
                
                # Validate jpylyzer output against schema                
                schemaValidationResult = schematron.validate(resultJpylyzerLXML)
                f.close()
                report = schematron.validation_report
                               
            except:
                status="fail"
                description="Schematron validation resulted in an error"
                ptOutString +=description + lineSep
            
            # Parse output of Schematron validation and extract interesting bits
            try:
                               
                reportAsXML = etree.tostring(report)
                            
                #for elem in root.iter():
                for elem in report.iter():
                    if elem.tag == "{http://purl.oclc.org/dsdl/svrl}failed-assert":
                        
                        status="fail"
                        
                        # Extract test definition
                        test = elem.get('test')
                        ptOutString += 'Test "'+ test + '" failed (' 
                        
                        # Extract text description from text element
                        for subelem in elem.iter():
                            if subelem.tag=="{http://purl.oclc.org/dsdl/svrl}text":
                               description=(subelem.text)
                               ptOutString +=description + ")" + lineSep
            except Exception:
                status="fail"
                description="Error processing Probatron output"
                ptOutString +=description + lineSep
            
            # Parse jpylyzer XML output and extract info on failed tests in case
            # image is not valid JP2
            try:
                #tree=ET.parse(nameJpylyzer)
                tree = resultJpylyzer
                root = resultJpylyzer.getroot()
                #validationOutcome=root.find("isValidJP2").text
                validationOutcome=root.find("isValidJP2").text
                                
                if validationOutcome=="False":
                    #testsElt=root.find('tests')
                    testsElt=root.find('tests')
                    ptOutString += "*** Jpylyzer JP2 validation errors:" +lineSep
                    # Jpylyzer errors reported as raw XML, this a bit ugly but works.
                    #ptOutString += ET.tostring(testsElt, encoding="ascii", method="xml") + lineSep
                
                    # Iterate over tests element and report names of all tags that
                    # correspond to tests that failed
                    
                    tests = list(testsElt.iter())
                    
                    for i in tests:
                        if i.text=="False":
                            ptOutString += "Test " + i.tag + " failed" + lineSep
                            
            except:
                description="Error processing Jpylyzer output"
                ptOutString +=description + lineSep
                                                        
        if status=="fail":

            fFailed.write(myJP2 + lineSep)
            fFailed.write("*** Schema validation errors:"+lineSep)
            fFailed.write(ptOutString)
            fFailed.write("####" + lineSep)
            
        statusLine=myJP2 +"," + status + lineSep
        
        #f_out.write(bytes(s, 'UTF-8'))
        fStatus.write(statusLine)
    
    end = time.clock()

    # Close output files
    fStatus.close()
    fFailed.close()
        
    print("jprofile ended: " + time.asctime())
    
    # Elapsed time (seconds)
    timeElapsed = end - start
    timeInMinutes = timeElapsed / 60
   
    print("Elapsed time: "+ str(timeInMinutes) + " minutes")
    

if __name__ == "__main__":
    main()
