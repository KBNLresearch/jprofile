# Jprofile
Johan van der Knijff, KB/National Library of the Netherlands.

## What is *jprofile*?
*Jprofile* is a simple tool for automated profiling of large batches of *JP2* images. Internally it wraps around [*jpylyzer*](http://www.openplanetsfoundation.org/software/jpylyzer), which is used for validating each image and for extracting its properties. The *jpylyzer* output is then validated against a set of [*Schematron*](http://en.wikipedia.org/wiki/Schematron) schemas that contain the required characteristics for master, access and target images, respectively. This is done through the [*Probatron4J*](http://www.probatron.org/) validator, which is wrapped inside *jprofile* as well.

## Dependencies
You will need *Java* 5 or more recent for running *Probatron4J*. (This is based on *Probatron4J*'s documentation. Some tests indicate possible misbehaviour under *Java* 5;  *Java* 6 appears to work fine.) All other dependencies ([*jpylyzer*](http://www.openplanetsfoundation.org/software/jpylyzer), [*Probatron*](http://www.probatron.org/)) are included with *jprofile*. The *Probatron* *JAR* file was taken from:

[http://www.probatron.org/probatron4j.html](ttp://www.probatron.org/probatron4j.html)

*Probatron4J*'s source code is available here:

[http://code.google.com/p/probatron4j/source/browse/#svn/trunk/](http://code.google.com/p/probatron4j/source/browse/#svn/trunk/)

## Licensing
*Jprofile* is released under the [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0). [*Probatron*](http://www.probatron.org/) is released under the [GNU Affero 3.0 license](http://www.gnu.org/licenses/agpl-3.0.html).

## Installation
Just unzip the contents of *jprofile_x.y.z_win32.zip* to any empty directory. Then open the configuration file ('*config.xml*') in a text editor and update the value of *java* to the location of *java* on your PC if needed.


## Command-line syntax

`
usage: jprofile batchDir prefixOut [-p PROFILE | -l]
`

## Positional arguments

**batchDir**: root directory of batch  

**prefixOut**: prefix that is used for writing output files

**PROFILE**: name of profile that defines schemas for master, access and target images 

Use the *-l* switch to list all available profiles (the *-p* and *-l* switches are mutually exclusive, i.e. you can use only one of them at the same time).

## Profiles
A *profile* is an *XML*-formatted file that simply defines which schemas are used to validate *jpylyzer*'s output for master, access and target images, respectively. Here's an example:

    <profile>
    
    <!-- Sample profile -->
       
    <schemaMaster>master300Gray.sch</schemaMaster>
    <schemaAccess>access150Colour.sch</schemaAccess>
    <schemaTarget>master300Colour.sch</schemaTarget>
    
    </profile>

Note that each entry only contains the *name* of a profile, not its full path! All profiles are located in the *profiles* directory in the installation folder.

###Available profiles

The following profiles are included by default:

| Name|Description|
| ------| -----:|
| kb_bt300.xml|Books and periodicals, master digitised at 300 ppi |
| kb_bt600.xml|Books and periodicals, master digitised at 600 ppi |
| kb_kranten.xml|Newspapers |
| kb_micro.xml|Microfilm|

It is possible to create custom-made profiles. Just add them to the *profiles* directory in the installation folder.
      

## Schemas
The quality assessment is based on a number of rules/tests that are defined a set of *Schematron* schemas. These are located in the *schemas* folder in the installation directory. In principe *any* property that is reported by *jpylyzer* can be used here, and new tests can be added by editing the schemas. More details on this can be found in [this blog post](http://www.openplanetsfoundation.org/blogs/2012-09-04-automated-assessment-jp2-against-technical-profile).  
 
###Available schemas
| Name|Description|
| ------| -----:|
| kbMaster.sch|Generic schema for losslessly-compressed master images |
| master300Colour.sch|Schema for losslessly-compressed master images, 300 ppi, Adobe RGB (1998) colour space|
| master600Colour.sch|Schema for losslessly-compressed master images, 600 ppi, Adobe RGB (1998) colour space|
| master300Gray.sch|Schema for losslessly-compressed master images, 300 ppi, Gray Gamma 2.2 colour space|
| master600Gray.sch|Schema for losslessly-compressed master images, 600 ppi, Gray Gamma 2.2 colour space|
| kbAccess.sch|Generic schema for lossily-compressed access images |
| access150Colour.sch|Schema for losslessly-compressed master images, 150 ppi, Adobe RGB (1998) colour space|
| access300Colour.sch|Schema for losslessly-compressed master images, 300 ppi, Adobe RGB (1998) colour space|
| access150Gray.sch|Schema for losslessly-compressed master images, 150 ppi, Gray Gamma 2.2 colour space|
| access300Gray.sch|Schema for losslessly-compressed master images, 300 ppi, Gray Gamma 2.2 colour space|

It is possible to create custom-made schemas. Just add them to the *schemas* directory in the installation folder.

## Usage examples

###List available profiles

`jprofile d:\myBatch mybatch -l`

This results in a list of all available profiles (these are stored in the installation folder's *profiles* directory):

    kb_bt300.xml
    kb_bt600.xml
    kb_kranten.xml
    kb_micro.xml

###Analyse batch
`jprofile d:\myBatch mybatch -p kb_bt300.xml`

This will result in the creation of 2 output files:

- `mybatch_status.csv` (status output file)
- `mybatch_failed.txt` (detailed output on images that failed quality asessment)

## Status output file
This is a comma-separated file with the assessment status of each analysed image. The assessment status is either *pass* (passed all tests) or *fail* (failed one or more tests). Here's an example:

<pre>
F:\test\access\MMKB03_000004896_00015_access.jp2,pass
F:\test\access\MMKB03_000004896_00115_access.jp2,pass
F:\test\access\MMKB03_000004896_00215_access.jp2,pass
F:\test\targets-jp2\MMKB03_MTF_RGB_20120626_02_01.jp2,fail
F:\test\master\MMKB03_000004896_00015_master.jp2,pass
</pre> 


## Failure output file
Any image that failed one or more tests are reported in the failure output file. For each failed image, it contains a full reference to the file path, followed by the specific errors. An example:

<pre>
F:\test\targets-jp2\MMKB03_MTF_RGB_20120626_02_01.jp2
*** Schema validation errors:
Test "layers = '1'" failed (wrong number of layers)
Test "transformation = '5-3 reversible'" failed (wrong transformation)
Test "comment = 'KB_MASTER_LOSSLESS_21/01/2011'" failed (wrong codestream comment string)
####
</pre>

Entries in this file are separated by a sequence of 4 '#' characters. Note that each line here corresponds to a failed test in the schema (this information is taken from *Probatron*'s output). For images that are identified as not-valid JP2 some additional information from *jpylyzer*'s output is included as well. For example:

<pre>
F:\test\master\MMUBL07_MTF_GRAY_20121213_01_05.jp2
*** Schema validation errors:
Test "isValidJP2 = 'True'" failed (no valid JP2)
*** Jpylyzer JP2 validation errors:
Test methIsValid failed
Test precIsValid failed
Test approxIsValid failed
Test foundNextTilePartOrEOC failed
Test foundEOCMarker failed
####
</pre>

Here, the outcome of test *isValidJP2* means that the image does not conform to the *JP2* specification. The lines following 'Jpylyzer JP2 validation errors' lists the specific errors that were reported by *jpylyzer*. The meaning of these errors can be found in the *jpylyzer* User Manual.



## Preconditions
- All images that are to be analysed have a .jp2 extension (all others are ignored!)
- *Master* images are located in a (subdirectory of a) directory called '*master*'
- *Access* images are located in a (subdirectory of a) directory called '*access*'
- *Target* images are located in a (subdirectory of a) directory called '*targets-jp2*'.

Other than that, the organisation of images may follow any arbitrary directory structure (*jprofile* does a recursive scan of whole directory tree of a batch)

##Known limitations
- *Jprofile* currently only runs under Windows
- Code is currently not compatible with *Python 3* (tested under *Python 2.7*; *Windows* executables are completely stand-alone).
- Images that have names containing square brackets ("[" and "]" are ignored (limitation of *Python*'s *glob* module, will be solved in the future).

##Useful links
- [*jpylyzer*](http://www.openplanetsfoundation.org/software/jpylyzer)
- [*Schematron*](http://en.wikipedia.org/wiki/Schematron)
- [*Probatron*](http://www.probatron.org/)
- [Automated assesment of JP2 against a technical profile using jpylyzer and Schematron](http://www.openplanetsfoundation.org/blogs/2012-09-04-automated-assessment-jp2-against-technical-profile)


