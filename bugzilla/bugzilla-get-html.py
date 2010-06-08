#!/usr/bin/python

import sys
import os
import getopt
import urllib
import time

def isInvalid(page,id):
  for l in page.split('\n'):
    if "Bug #"+str(id)+"" in l:
      return True
  return False

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
      if "<p>Bugzilla &ndash; Invalid Bug ID</p>" in l:
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
      print url
    return page
  
  def hasNext(self):
    return self.currentPage != None
    
  def next(self):
    cpage = self.currentPage
    cid = self.currentid - 1
    self.currentPage = self.getPage()
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


def extract(baseurl,downloaddir,delay=1):
  bugIterator = BugIterator(baseurl,pageIterator)
  while (bugIterator.hasNext()):
    p = bugIterator.next()
    retrySave(baseurl,p,downloaddir,delay)

baseurl = "https://bugs.eclipse.org/bugs"
downloaddir = ""


if __name__ == "__main__":
  arguments = sys.argv[1:]
  optlist, args = getopt.getopt(arguments, 'd:')
  print optlist
  for o, a in optlist:
    if o in ['-d','downloaddir=']:
      downloaddir = a
  extract(baseurl,groupid,atid,downloaddir,1)