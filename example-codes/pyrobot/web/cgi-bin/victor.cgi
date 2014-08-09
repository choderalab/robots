#!/usr/bin/python

import cgi
import cgitb; cgitb.enable()

import os, sys
# Store current working directory
dn = os.path.dirname(os.path.realpath(__file__))
# Append current directory to the python path
sys.path.append(os.path.join(dn, 'victor'))
from victor_parser import VictorParser
from database import MySQLDatabase, SqliteDatabase

print 'Content-Type: text/html'     # HTML is following
print                               # blank line, end of headers
print '<title>Victor results uploader</title>'
print '<html><body><center>'
print '<h1>Welcome to the Victor Results Uploader</h1>'
print '<a href="http://en.wikipedia.org/wiki/Victor_Hugo"><img src="/600full-victor-hugo.gif"></a></br></br></br>'
form = cgi.FieldStorage()

# Get filename here.
fileitem = form['filename']

# Test if the file was uploaded
if fileitem.filename:
    # strip leading path from file name to avoid 
    # directory traversal attacks
    fn = os.path.basename(fileitem.filename)
    db = MySQLDatabase(host='hldbv02', user='ronm', port=3306, passwd='a1a1a1', db='tecan')
    exp_id = VictorParser.ImportFileToDB(fileitem.file, db)
    href = '/RoboSite/Exp/%s/0' % exp_id
    print '<h2>Success!</h2>'
    print 'The file %s was uploaded to the database </br>' % fn
    print 'The ID for this experiment is <a href="%s">%s</a> </br>' % (href, exp_id)
else:
    print '<h2>Error</h2>'
    print 'No file was uploaded</br>'
    print '<script type="text/javascript"></script><a href="javascript:history.back(-1)">Go Back</a>'

print '</center></body></html>'
