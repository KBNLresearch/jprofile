@echo off
setlocal

::::::::: CONFIGURATION :::::::::: 

:: Script base name (i.e. script name minus .py extension)
set scriptBaseName=jprofile

:: Python
set python=c:\python27\python

:: Path to PyInstaller
set pathPyInstaller=c:\pyinstall\

:: Path to 7-zip command-line tool
set zipCommand="C:\Program Files\7-Zip\7z"

:: Executes jpylyzer with -v option and stores output to 
:: env variable 'version'
set vCommand=%python% %scriptBaseName%.py -v
%vCommand% 2> temp.txt
set /p version= < temp.txt
del temp.txt 

::::::::: BUILD :::::::::::::::::: 

:: Make spec file
%python% %pathPyInstaller%\MakeSpec.py %scriptBaseName%.py

:: Build binaries
%python% %pathPyInstaller%\build.py %scriptBaseName%.spec

:: Create probatron, doc profiles and schemas dirs in dist dir
md .\dist\%scriptBaseName%\probatron
md .\dist\%scriptBaseName%\doc
md .\dist\%scriptBaseName%\profiles
md .\dist\%scriptBaseName%\schemas

:: Copy files to dist directory
copy /Y .\probatron\* .\dist\%scriptBaseName%\probatron\
copy /Y .\doc\* .\dist\%scriptBaseName%\doc\
copy /Y .\profiles\* .\dist\%scriptBaseName%\profiles\
copy /Y .\schemas\* .\dist\%scriptBaseName%\schemas\
copy /Y .\config.xml .\dist\%scriptBaseName%\config.xml

:: Create doc directory in dist directory
md .\dist\%scriptBaseName%\doc

:: Generate name for ZIP file
set zipName=%scriptBaseName%_%version%_win32.zip

:: Create ZIP file
%zipCommand% a -r %zipName% .\dist\%scriptBaseName%\*

:: Delete dist directory that was created by PyInstaller
::rmdir dist /S /Q

md win32

:: Move ZIP file to win32 directory
move /Y %zipName% .\win32\

::::::::: CLEANUP ::::::::::::::::: 

:: Delete build directory
rmdir build /S /Q

:: Delete dist directory
rmdir dist /S /Q

:: Rename Win32 directory to dist
ren win32 dist

:: Delete spec file
del %scriptBaseName%.spec

echo /
echo Done! Created %zipName% in directory .\dist\!
echo / 

