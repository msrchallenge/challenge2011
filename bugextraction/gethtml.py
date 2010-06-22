import sys
import os
import getopt

from bugiter.chromeBugIterator import ChromeBugIterator
from bugiter.bugzillaBugIterator import BugzillaBugIterator
from bugiter.sourceForgeBugIterator import SourceForgeBugIterator

def savePage(name,directory,content):
  if not os.path.exists(directory):
    os.mkdir(directory)
  f = open(directory+'/'+name,'w')
  f.write(content)
  f.close()


def getHTML(bugIterator,baseurl,startid,endid,downloaddir,delay=1):
  while (bugIterator.hasNext()):
    p = bugIterator.next()
    savePage(baseurl,p,downloaddir,delay)

def chrome(baseurl,startid,endid,downloaddir,delay=1):
  getHTML(chromeBugIterator(baseurl,startid,endid,delay))

def bugzilla(baseurl,startid,endid,downloaddir,delay=1):
  getHTML(bugzillaBugIterator(baseurl,startid,endid,delay))

def sourceforge(baseurl,startid,endid,downloaddir,delay=1):
  groupid = baseurl.split('=')[0].split('&')[0]
  atid = baseurl.split('=')[1]
  getHTML(sourceForgeBugIterator(baseurl,startid,endid,delay,groupid,atid))

def usage():
  sys.stderr.write(sys.argv[0] + " -s/--startid [arg] -e/--endid [arg] -d/--downloaddirectory [arg] --sourceforge --bugzilla --chrome\n")
  sys.exit(0)

def trackerCheck():
  if trackertype != None:
    sys.stderr.write('you can only provide one bug tracker type\n')
    sys.exit(0)

baseurl = None #"http://code.google.com/p/chromium/issues/detail?id="
downloaddir = None #""
startid = None #-1
endid = None #-1
trackertype = None
delay = 1

register = {}
register['bugzilla']    = bugzilla
register['chrome']      = chrome
register['sourceforge'] = sourceforge

if __name__ == "__main__":
  arguments = sys.argv[1:]
  optlist, args = getopt.getopt(arguments, 's:e:d:',['delay=','startid=','endid=','downloaddirectory=','sourecforge','bugzilla','chrome'])
  for o, a in optlist:
    if o in ['-d','--downaloddirectory']:
      downloaddir = a
    if o in ['-s','--startid']:
      startid = int(a)
    if o in ['-e','--endid']:
      endid = int(a)
    if o in ['--sourceforge']:
      trackerCheck()
      trackertype = 'soruceforge'
    if o in ['--bugzilla']:
      trackerCheck()
      trackertype = 'bugzilla'
    if o in ['--chrome']:
      trackerCheck()
      trackertype = 'chrome'
    if o in ['--delay']:
      delay = int(a)
  if delay<0 or startid<0 or endid<0 or or startid==None or endid==None or trackertype==None:
    usage()
  register[trackertype](baseurl,startid,endid,downloaddir,delay)  
