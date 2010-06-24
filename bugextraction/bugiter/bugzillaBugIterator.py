import time
import sys

from ABugIterator import ABugIterator

class BugzillaBugIterator(ABugIterator):
  def __init__(self,baseurl,startid,endid,delay=2):
    self.baseurl = baseurl
    self.currentid = startid
    self.endid = endid
    self.delay = delay

  def init(self):
    self.currentPage = self.getPage(self.delay)
  
  def isInvalid(self,page,id):
    for l in page.split('\n'):
      if "Invalid Bug ID</p>" in l or "Bug #"+str(id)+" does not exist." in l:
        return True
    return False

  def write(self,write,p,downloaddir):
    write( str(p[0])+".html",downloaddir,p[1] )
    write( str(p[0])+"-history.html",downloaddir, self.retryFetchPage( self.baseurl + "/show_activity.cgi?id=" + str(p[0]),self.delay) )
  
  def getPage(self,delay):
    flag = True
    page = None
    while flag and self.currentid <= self.endid :
      url = self.baseurl + "/show_bug.cgi?id=" + str(self.currentid)
      self.currentid += 1
      page = self.retryFetchPage(url,delay)
      flag = self.isInvalid(page,self.currentid-1)
      time.sleep(delay)
      if flag:
        sys.stderr.write("No BugId - " + str(self.currentid-1) + "\n")
    if flag:
      page = None
    return page
  
  def hasNext(self):
    return self.currentPage != None
    
  def next(self):
    cpage = self.currentPage
    cid = self.currentid - 1
    self.currentPage = self.getPage(self.delay)
    return (cid,cpage)

