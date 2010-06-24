#!/usr/bin/python

import time
from ABugIterator import ABugIterator

#########################################################################
class PageIterator:
  def __init__(self,baseurl,groupid,atid,delay):
    self.baseurl = baseurl
    self.delay = delay
    self.groupid = groupid
    self.atid = atid
    self.nextUrl = baseurl + "/tracker/?group_id="+str(groupid)+"&atid="+str(atid)
  
  def init(self):
    return True

  def hasNext(self):
    return self.nextUrl != None
      
  def next(self):
    print "Next page"
    page = ABugIterator.retryFetch(self.nextUrl,self.delay)
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
class SourceForgeBugIterator(ABugIterator):
  def __init__(self,baseurl,startid,endid,delay,groupid,atid):
    raise "Need to implment start and end id"
    self.baseurl = baseurl
    self.i = 0
    self.urls = []
    self.delay=delay
    self.startid = int(startid)
    self.endid = int(endid)

  def init(self):
    self.pageIterator = PageIterator(baseurl,groupid,atid,delay)  

  def write(self,write,p,downloaddir):
    write( str(p[0])+".html",downloaddir,p[1] )

  def fetchUrls(self,page):
    urls = []
    for l in page.split('\n'):
      if "&aid=" in l:
        tokens = l.split('"')
        bugurl = self.baseurl + tokens[len(tokens)-2]
        ts = tokens[len(tokens)-2].split('aid=')
        ts = ts[1].split('&gr')
        bugid = str(int(ts[0]))
        if int(bugid) > self.startid or int(bugid) < self.endid:
          urls.append((bugid,bugurl))
    return urls
    
  def hasNext(self):
    return self.pageIterator.hasNext()
    
  def next(self):
    if len(self.urls) > self.i:
      self.i = self.i + 1
      return (self.urls[self.i-1][0],self.retryFetch(self.urls[self.i-1][1],self.delay))
    self.i = 0
    self.urls = self.fetchUrls(self.pageIterator.next())
    return self.next()
      
    
