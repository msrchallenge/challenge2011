#!/usr/bin/python

import time
from ABugIterator import ABugIterator

class bugzillaBugIterator(ABugIterator):
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
      page = self.retryFetchPage(url,delay)
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

