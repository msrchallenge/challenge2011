#!/usr/bin/python

import time
from ABugIterator import ABugIterator

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
    page = ABugIterator.retryFetch(self.nextUrl,0)
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
class BugIterator(ABugIterator):
  def __init__(self,baseurl,startid,endid,delay,groupid,atid):
    raise "Need to implment start and end id"
    self.baseurl = baseurl
    self.pageIterator = PageIterator(baseurl,groupid,atid)
    self.i = 0
    self.urls = []
    self.delay=delay
  
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
      self.i = self.i + 1
      return (self.urls[self.i-1][0],self.retryFetch(self.urls[self.i-1][1],self.delay))
    self.i = 0
    self.urls = self.fetchUrls(self.pageIterator.next())
    return self.next()
      
    
