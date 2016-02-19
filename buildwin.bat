:
:: Build Windows jprofile binaries from Python script, and pack them in ZIP file
::
:: Johan van der Knijff, 1 December 2014
::
:: Dependencies:
:: 
:: - Python 2.7  (PyInstaller doesn't work with Python 3 yet!) 
:: - PyInstaller 2: http://www.pyinstaller.org/
:: - PyWin32 (needed by PyInstaller): http://sourceforge.net/projects/pywin32/files/
:: - a spec file
::
:: IMPORTANT: To build 32 bit binaries you need a 32 bit version of both Python and PyWin32! Can be installed
:: alongside a 64 install, so this shouldn't be a big deal.

::
@echo off
setlocal

::::::::: CONFIGURATION :::::::::: 

:: Path to 32 bit Python
set python=c:\python27_32bit\python
::set python=c:\python27\python

:: Path to PyInstaller
set pathPyInstaller=c:\pyinstall\

:: Path to 7-zip command-line tool
set zipCommand="C:\Program Files\7-Zip\7z"

:: Script base name (i.e. script name minus .py extension)
set scriptBaseName=jprofile

:: PyInstaller spec file that defines build options
set specFile=jprofile_win.spec

:: Directory where build is created (should be identical to 'name' in 'coll' in spec file!!)
set distDir=.\dist_win\

:: Executes jprofile with -v option and stores output to 
:: env variable 'version'
set vCommand=%python% .\%scriptBaseName%\%scriptBaseName%.py -v
%vCommand% 2> temp.txt
set /p version= < temp.txt
del temp.txt 

::::::::: BUILD :::::::::::::::::: 

:: Build binaries
%python% %pathPyInstaller%\pyinstaller.py --debug %specFile%

:: Generate name for ZIP file
set zipName=%scriptBaseName%_%version%_win.zip

:: Create ZIP file
%zipCommand% a -r %distDir%\%zipName% %distDir%\%scriptBaseName%
:: disabled for now as zipdir doesn't properly handle nested dir with xslt stuff
::%python% .\zipdir.py %distDir%\%scriptBaseName% %distDir%\%zipName% 

::::::::: CLEANUP ::::::::::::::::: 

:: Delete build directory
rmdir build /S /Q

:: Delete jprofile directory in distdir
rmdir %distDir%\%scriptBaseName% /S /Q

::::::::: PARTY TIME! ::::::::::::::::: 

echo /
echo Done! Created %zipName% in directory %distDir%!
echo / 
