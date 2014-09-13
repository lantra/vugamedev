# Author: Aaron R. Short
# Date: April 10, 2009
# File: comparison.py
# This is a quick hack to find which files, packages, and or modules didn't
# make it over in py2exe setup. To use unzip your libary.zip so that the
# directories should be similar. Also if you don't clear your build directory
# every run you might want to delete that as well.

import os
import glob
import string

sourcepath = '\src'
distpath = '\dist'

sourcelist = []
    
for root, dirs, files in os.walk(sourcepath):
    for name in files:
        pathfile = os.path.join(root, name)
        
        #ignore python extensions
        pathfile = string.replace(pathfile, '.pyo', '') 
        pathfile = string.replace(pathfile, '.pyc', '')
        pathfile = string.replace(pathfile, '.py', '')
        #remove root path
        pathfile = string.replace(pathfile, sourcepath, '') 
        sourcelist.append(pathfile)

distlist = []
    
for root, dirs, files in os.walk(distpath):
    for name in files:
        pathfile = os.path.join(root, name)
        
        #ignore python extensions
        pathfile = string.replace(pathfile, '.pyo', '') 
        pathfile = string.replace(pathfile, '.pyc', '')
        pathfile = string.replace(pathfile, '.py', '')
        
        #remove root path      
        pathfile = string.replace(pathfile, distpath, '')   
        distlist.append(pathfile)

sourceset = set(sourcelist)
distset = set(distlist)

missing = sourceset - distset        

for (files) in sorted(missing):
    print files