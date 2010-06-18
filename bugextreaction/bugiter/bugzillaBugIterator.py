#!/usr/bin/python

import sys
import os
import getopt
import urllib
import time

#########################################################################
class BugIterator:
  def __init__(self,baseurl,startid,endid,delay=2):
    self.baseurl = baseurl
    self.currentid = startid
    self.endid = endid
    self.delay = delay
    self.currentPage = self.getPage(delay)
  
  def isInvalid(self,page,id):
    for l in page.split('\n'):
      if "Invalid Bug ID</p>" in l:
        return True
    return False
  
  def getPage(self,delay):
    flag = True
    page = None
    while flag and self.currentid <= self.endid :
      url = self.baseurl + "/show_bug.cgi?id=" + str(self.currentid)
      self.currentid += 1
      page = retryFetchPage(url)
      flag = self.isInvalid(page,self.currentid-1)
      time.sleep(delay)
      if not flag:
        print "No BugId - " + str(self.currentid-1)
    if flag:
      page = None
    else:
      print "BugId - " + str(self.currentid-1)
    return page
  
  def hasNext(self):
    return self.currentPage != None
    
  def next(self):
    cpage = self.currentPage
    cid = self.currentid - 1
    self.currentPage = self.getPage(self.delay)
    return (cid,cpage)
      
#########################################################################    

def retryFetchPage(url,delay=1):
  try:
    sock = urllib.urlopen(url)
    source = sock.read()
    sock.close()
    return source
  except Exception:
    time.sleep(delay)
    return retryFetchPage(url,delay+1)


def savePage(name,directory,content):
  if not os.path.exists(directory):
    os.mkdir(directory)
  f = open(directory+'/'+name,'w')
  f.write(content)
  f.close()

def retrySave(baseurl,p,downlaoddir,delay):
  try:
    savePage(str(p[0])+"-history.html",downlaoddir,retryFetchPage(baseurl+"/show_activity.cgi?id="+str(p[0])))
    savePage(str(p[0])+".html",downlaoddir,p[1])
    time.sleep(delay) # sleep delay seconds
  except Exception:
    time.sleep(delay+1)
    retrySave(baseurl,p,downlaoddir,delay)


def extract(baseurl,startid,endid,downloaddir,delay=1):
  bugIterator = BugIterator(baseurl,startid,endid)
  while (bugIterator.hasNext()):
    p = bugIterator.next()
    retrySave(baseurl,p,downloaddir,delay)

baseurl = "https://bugs.eclipse.org/bugs"
downloaddir = ""
startid = -1
endid = -1

if __name__ == "__main__":
  arguments = sys.argv[1:]
  optlist, args = getopt.getopt(arguments, 's:e:d:')
  for o, a in optlist:
    if o in ['-d']:
      downloaddir = a
    if o in ['-s']:
      startid = int(a)
    if o in ['-e']:
      endid = int(a)
  if startid<0 or endid<0:
    sys.stderr.write("startid [-s] and endid [-e] need to be provided and be greater than -1")
    sys.exit(0)
  if len(args) == 0:
    print "getting Eclipse bugs"
  else:
    baseurl = args[0]
  if len(args) > 1:
    sys.stderr.write("at most one base url needs to be provided")
    sys.exit(0)
  extract(baseurl,startid,endid,downloaddir,1)
