import sys
import getopt
import os
from ABug import ABug
from .util.FileIterator import FileIterator


class ChromeBugreport(ABug):
  def __init__(self,textlines,bugid):
    if hasattr(ABug, '__init__'):
      ABug.__init__(self)
    self.lines = textlines
    self.addAttribute("bugid",bugid)
    self.namedict = {}
    self.namedict['Summary'] = 'shortdesc'
    self.namedict['Status'] = 'status'
    self.namedict['Labels'] = 'label'
    self.namedict['Owner'] = 'assigned'
    self.namedict['Cc'] = 'cc'
    self.namedict['Mergedinto'] = 'merge'
    self.namedict['Blockedon'] = 'blocked-by'
    self.namedict['Blocks'] = 'blocks'
    
  def readChanges(self,j,lines):
    date = self.comments[-1][0]
    commenter = self.comments[-1][1]
    if '<div class="updates">' in lines[j+3]: 
      changes = lines[j+8].replace("\n","").split("<br>")
      for change in changes:
        if len(change)>1:
          cfield = self.namedict[ change.split('<b>')[1].split(':</b>')[0] ]
          cvalue = change.split('</b> ')[1]
          if cfield == "label" or cfield == "cc" or cfield == "blocks" or cfield == "blocked-by":
            for label in cvalue.split(" "):
              if len(label) > 1:
                ovalue = ""
                nvalue = ""
                if label == '-':
                  ovalue = label
                else:
                  nvalue = label
                self.addChange((cfield,nvalue,ovalue,commenter,date))  
          elif cfield == "merge":
            ovalue = change.split('</b> ')[1]
            self.addChange((cfield,ovalue,ovalue,commenter,date))
          else:
            nvalue = None
            ovalue = change.split('</b> ')[1]
            self.addChange((cfield,nvalue,ovalue,commenter,date))
    
  def readComment(self,i,lines):
    if '<span class="author">Comment <a name=' in lines[i]:
      date = lines[i+4].split('"')[3]
      commenter = lines[i+3].replace('\n','')
      comment = []
      j = i + 7
      while not "</pre>" in lines[j]:
        comment.append(lines[j])
        j+=1
      self.addComment((date,commenter,comment))
      self.readChanges(j,lines)
    
  def readAttachments(self,i,lines):
    if '<div class="attachments">' in lines[i]:
      j = i + 12
      cfile = None
      cdesc = ""
      clink = None
      while not "</div>" in lines[j]:
        if '<b >' in lines[j]:
          cfile = lines[j].split('>')[1].split('<')[0]
        if '>Download</a>' in lines[j]:
          clink = lines[j].split('"')[1].replace("amp&","")
          self.addAttachment( (cfile,cdesc,clink) )
        j += 1
    
  def readCreator(self,i,lines):
    if '<div class="author">' in lines[i]:
      self.addAttribute("creator"     , lines[i+1].replace("Reported by ",""))
      self.addAttribute("creationDate", lines[i+1].split('"')[3])

  def readAssigned(self,i,lines):
    if '<tr><th align="left">Owner:&nbsp;</th><td>' in lines[i]:
      self.addAttribute("assigned", lines[i+2])

  def readLabel(self,i,lines):
    if '<a href="list?q=label:' in lines[i] and not '<tr><td colspan="2">' in lines[i]:
      if not self.attributes.has_key("label"):
        self.addAttribute("label",[])
      self.addAttribute("label",lines[i].split('"')[1].split(":")[1] + lines[i+1].split('"')[1])

  def readCCs(self,i,lines):
    if '<tr><th class="vt" align="left">Cc:&nbsp;</th><td>' in lines[i]:
      if not self.attributes.has_key("cc"):
        self.addAttribute("cc",[])
      j = i+3
      while not "</td>" in lines[j]:
        for cc in lines[j].split(",  "):
          self.addAttribute("cc",cc)
        j += 1    

  def readStatus(self,i,lines):
    if '<tr><th align="left">Status:&nbsp;</th>' in lines[i]:
      if len(lines[i+3]) > 4:
        self.addAttribute("status",lines[i+3].split(">")[1] + " -- " + lines[i+3].split('"')[1])
      else:
        self.addAttribute("status","")

  def readShortdesc(self,i,lines):
    if 'Issue <a href="detail?id=' in lines[i]:
      self.addAttribute("shortdesc",lines[i+3].split(">")[1].split("<")[0])

  def readLongdesc(self,i,lines):
    if '<td class="vt issuedescription" width="100%">' in lines[i]:
      j = i+7
      self.addAttribute("longdesc",[])
      while not '</pre>' in lines[j]:
        self.addAttribute("longdesc",lines[j])
        j += 1

  def readBlockedBy(self,i,lines):
    if '<br><b>Blocked on:</b><br>' in lines[i]:
      j = i+7
      if not self.attributes.has_key('blocked-by'):
        self.addAttribute('blocked-by',[])
      while not '</div>' in lines[j]:
        if 'issue' in lines[j]:
          self.addAttribute('blocked-by',lines[j].split(' ')[1].split('<')[0])
        j+=1

  def readBlocks(self,i,lines):
    if '<br><b>Blocking:</b><br>' in lines[i]:
      j = i
      if not self.attributes.has_key('blocks'):
        self.addAttribute('blocks',[])
      while not '</div>' in lines[j]:
        if 'issue' in lines[j]:
          self.addAttribute('blocks',lines[j].split(' ')[1].split('<')[0])
        j += 1

  def read(self):
    i = 0
    while i < len(self.lines):
      self.readCreator(i,self.lines)
      self.readAssigned(i,self.lines)
      self.readLabel(i,self.lines)
      self.readCCs(i,self.lines)
      self.readStatus(i,self.lines)
      self.readShortdesc(i,self.lines)
      self.readLongdesc(i,self.lines)
      self.readBlockedBy(i,self.lines)
      self.readBlocks(i,self.lines)
      self.readComment(i,self.lines)
      self.readAttachments(i,self.lines)
      i += 1
      
  def completeChanges(self):
    c = {}
    c['shortdesc'] = self.attributes['shortdesc']
    c['status'] = self.attributes['status']
    c['assigned'] = self.attributes['assigned']
    i = 0
    while i < len(self.changes):
      change = self.changes[i]
      if change[0] == 'shortdesc' or change[0] == 'status' or change[0] == 'assigned':
        t = change[2]
        self.changes[i] = (change[0],c[change[0]],change[2],change[3],change[4])
        c[change[0]] = t
      i += 1
