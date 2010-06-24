import sys
import os
import getopt
import time
from threading import Thread


from bugiter.chromeBugIterator import ChromeBugIterator
from bugiter.bugzillaBugIterator import BugzillaBugIterator
from bugiter.sourceForgeBugIterator import SourceForgeBugIterator

def savePage(name,directory,content):
  sys.stderr.write("Writing " + name + '\n')
  f = open(directory+'/'+name,'w')
  f.write(content)
  f.close()


class ExtractorThread(Thread):
  def __init__(self,iterator,baseurl,downloaddir,delay):
    Thread.__init__(self)
    self.iterator = iterator
    self.done = False
    self.baseurl = baseurl
    self.downloaddir = downloaddir
    self.delay = delay

  def run(self):
    self.iterator.init()
    while self.iterator.hasNext():
      p = self.iterator.next()
      self.iterator.write(savePage,p,self.downloaddir)
    self.done = True

def run(itergen,baseurl,startid,endid,downloaddir,delay,threadmax,idinc):
  threadc = 0
  currentid = startid
  threads = []
  try:
    os.makedirs(downloaddir)
  except OSError:
    print "error"
    pass
  # init
  while threadc < threadmax and currentid < endid:
    c = ExtractorThread( itergen(baseurl,currentid,currentid+idinc,delay),baseurl,downloaddir,delay )
    threads.append( c )
    c.start()
    sys.stderr.write("Started " + str(currentid) + " to " + str(currentid+idinc) + "\n")
    currentid = currentid+idinc+1
    threadc += 1
  while currentid < endid:
    i = 0
    while i < len(threads):
      if threads[i].done and currentid < endid:
        c = ExtractorThread( itergen(baseurl,currentid,currentid+idinc,delay),baseurl,downloaddir,delay )
        threads[i] = ExtractorThread( c )
        currentid = currentid+idinc+1
        c.start()
      i += 1
    time.sleep(1)
  while threadc > 0:
    threadc = 0
    for thread in threads:
      if thread.done:
        ct += 1
    time.sleep(1)


def chrome(baseurl,startid,endid,delay=1):
  return ChromeBugIterator(baseurl,startid,endid,delay)

def bugzilla(baseurl,startid,endid,delay=1):
  return BugzillaBugIterator(baseurl,startid,endid,delay)

def sourceforge(baseurl,startid,endid,delay=1):
  groupid = baseurl.split('=')[0].split('&')[0]
  atid = baseurl.split('=')[1]
  return SourceForgeBugIterator(baseurl,startid,endid,delay,groupid,atid)

def usage():
  sys.stderr.write(sys.argv[0] + " -s/--startid [arg] -e/--endid [arg] -d/--downloaddirectory [arg] -n/--number-threads [arg] --sourceforge --bugzilla --chrome\n")
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
nthreads = 1

register = {}
register['bugzilla']    = bugzilla
register['chrome']      = chrome
register['sourceforge'] = sourceforge

if __name__ == "__main__":
  arguments = sys.argv[1:]
  optlist, args = getopt.getopt(arguments, 's:e:d:n:',['number-threads=','delay=','startid=','endid=','downloaddirectory=','sourecforge','bugzilla','chrome'])
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
    if o in ['-n','--number-threads']:
      nthreads = int(a)
  if delay<0 or startid<0 or endid<0 or startid==None or endid==None or trackertype==None or len(args)!=1:
    usage()
  baseurl = args[0]
  run(register[trackertype],baseurl,startid,endid,downloaddir,delay,nthreads,1000)
