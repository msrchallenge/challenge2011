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
                if label[0] == '-':
                  ovalue = label[1:]
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
      commenter = lines[i+3].replace('\n','').replace('</span>,','')
      comment = []
      j = i + 7
      while not "</pre>" in lines[j]:
        comment.append(lines[j].replace('\r',''))
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
      self.addAttribute("creator"     , lines[i+1].replace("Reported by ","").replace(',','').replace('\n',''))
      self.addAttribute("creationDate", lines[i+2].split('"')[3])

  def readAssigned(self,i,lines):
    if '<tr><th align="left">Owner:&nbsp;</th><td>' in lines[i]:
      self.addAttribute("assigned", lines[i+2].replace("\n",""))

  def readLabel(self,i,lines):
    if '<a href="list?q=label:' in lines[i] and not '<tr><td colspan="2">' in lines[i]:
      if not self.attributes.has_key("label"):
        self.addAttribute("label",lines[i].split('"')[1].split(":")[1] + " -- " + lines[i+1].split('"')[1].replace('\n',''))
      else:
        self.addToAttribute("label","\n"+lines[i].split('"')[1].split(":")[1] + " -- " + lines[i+1].split('"')[1].replace("\n",''))

  def readCCs(self,i,lines):
    if '<tr><th class="vt" align="left">Cc:&nbsp;</th><td>' in lines[i]:
      j = i+3
      text = None
      while not "</td>" in lines[j]:
        for cc in lines[j].split(",  "):
          if len(lines[j].replace(' ',''))>3:
            if text == None:
              text = cc.replace('\n','')
            else:
              text += '\n' + cc.replace('\n','')
        j += 1    
      self.addAttribute("cc",text)

  def readStatus(self,i,lines):
    if '<tr><th align="left">Status:&nbsp;</th>' in lines[i]:
      if len(lines[i+3]) > 4:
        self.addAttribute("status",lines[i+3].split(">")[1].split("<")[0] + " -- " + lines[i+3].split('"')[1])
      else:
        self.addAttribute("status","")

  def readShortdesc(self,i,lines):
    if 'Issue <a href="detail?id=' in lines[i]:
      self.addAttribute("shortdesc",lines[i+3].split(">")[1].split("<")[0])

  def readLongdesc(self,i,lines):
    if '<td class="vt issuedescription" width="100%">' in lines[i]:
      j = i+7
      #self.addAttribute("longdesc",[])
      t = []
      while not '</pre>' in lines[j]:
        t.append(lines[j].replace('\n','').replace('\r',''))
        j += 1
      text = t[0]
      for tt in t[1:]:
        text += '\n'+ tt.replace('\n','')
      self.addAttribute("longdesc",text)

  def readBlockedBy(self,i,lines):
    if '<br><b>Blocked on:</b><br>' in lines[i]:
      j = i+7
      while not '</div>' in lines[j]:
        if 'issue' in lines[j] and not 'chromium-' in lines[j] and not '<a href="' in lines[j] and not 'class="closed_ref"' in lines[j] and not 'href="detail?id=' in lines[j]:
          import sys
          sys.stderr.write(self.attributes["bugid"] + " - " + lines[j-1] + lines[j] + lines[j+1])
          if not self.attributes.has_key('blocked-by'):
            self.addAttribute('blocked-by',lines[j].split('issue ')[1].split('<')[0].replace('\n',''))
          else:
            self.addToAttribute('blocked-by','\n'+lines[j].split('issue ')[1].split('<')[0].replace('\n',''))
        j+=1

  def readBlocks(self,i,lines):
    if '<br><b>Blocking:</b><br>' in lines[i]:
      j = i
      while not '</div>' in lines[j]:
        if 'issue' in lines[j] and not 'chromium-' in lines[j] and not '<a href="' in lines[j] and not 'class="closed_ref"' in lines[j] and not 'href="detail?id=' in lines[j]:
          if not self.attributes.has_key('blocks'):
            self.addAttribute('blocks',lines[j].split('issue ')[1].split('<')[0].replace('\n',''))
          else:
            self.addToAttribute('blocks','\n'+lines[j].split('issue ')[1].split('<')[0].replace('\n',''))
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
    c['shortdesc'] = ""
    c['status'] = 'Untriaged'
    c['assigned'] = self.attributes["creator"].split('>')[1].split('<')[0]
    i = 0
    while i < len(self.changes):
      change = self.changes[i]
      if change[0] == 'shortdesc' or change[0] == 'status' or change[0] == 'assigned':
        t = change[2]
        self.changes[i] = (change[0],change[2],c[change[0]],change[3],change[4])
        c[change[0]] = t
      i += 1
