#!/usr/bin/python

import sys
import os
import getopt
import urllib
import time

#########################################################################
class PageIterator:
  def __init__(self,baseurl,groupid,atid):
    self.baseurl = baseurl
    self.groupid = groupid
    self.atid = atid
    self.nextUrl = baseurl + "/tracker/?group_id="+str(groupid)+"&atid="+str(atid)
  
  def hasNext(self):
    return self.nextUrl != None
      
  def next(self):
    print "Next page"
    page = fetchPage(self.nextUrl)
    self.nextUrl = None
    for l in page.split('\n'):
      if "Next" in l:
        tokens = l.split('"')
        nexturl = baseurl + tokens[len(tokens)-2]
        nexturl = nexturl.replace('amp;','')
        self.nextUrl =  nexturl    
    return page
#########################################################################

#########################################################################
class BugIterator:
  def __init__(self,baseurl,pageIterator):
    self.baseurl = baseurl
    self.pageIterator = pageIterator
    self.i = 0
    self.urls = []
  
  def fetchUrls(self,page):
    urls = []
    for l in page.split('\n'):
      if "&aid=" in l:
        tokens = l.split('"')
        bugurl = self.baseurl + tokens[len(tokens)-2]
        ts = tokens[len(tokens)-2].split('aid=')
        ts = ts[1].split('&gr')
        bugid = int(ts[0])
        urls.append((bugid,bugurl))
    return urls
    
  def hasNext(self):
    return self.pageIterator.hasNext()
    
  def next(self):
    if len(self.urls) > self.i:
      print "BugId - " + str(self.urls[self.i][0])
      self.i = self.i + 1
      return self.urls[self.i-1]
    self.i = 0
    self.urls = self.fetchUrls(self.pageIterator.next())
    return self.next()
      
#########################################################################    

def fetchPage(url):
  sock = urllib.urlopen(url)
  source = sock.read()
  sock.close()
  return source

def savePage(name,directory,content):
  if not os.path.exists(directory):
    os.mkdir(directory)
  f = open(directory+'/'+name,'w')
  f.write(content)
  f.close()



def extract(baseurl,groupid,atid,downloaddir,delay=1):
  pageIterator = PageIterator(baseurl,groupid,atid);
  bugIterator = BugIterator(baseurl,pageIterator)

  while (bugIterator.hasNext()):
    p = bugIterator.next()
    savePage(str(p[0])+".html",downloaddir,fetchPage(p[1]))
    time.sleep(delay) # sleep delay seconds 

baseurl = "http://sourceforge.net"
groupid = None#157793
atid    = None#805242
downloaddir = ""
trackerurl = baseurl + "/tracker/?group_id="+str(groupid)+"&atid="+str(atid)



if __name__ == "__main__":
  arguments = sys.argv[1:]
  optlist, args = getopt.getopt(arguments, 'g:a:d:',['groupid=','atid=','downloaddir='])
  print optlist
  for o, a in optlist:
    if o in ['-g','groupid=']:
      groupid = int(a)
    if o in ['-a','atid=']:
      atid = int(a)
    if o in ['-d','downloaddir=']:
      downloaddir = a
  if groupid==None or atid==None:
    sys.stderr.write('Usage: ' + sys.argv[0] + ' -g groupid -a atid [-d downloaddir] \n')
    sys.exit(0)
  extract(baseurl,groupid,atid,downloaddir,1)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    