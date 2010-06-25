import string

from ABug import ABug
from .util.FileIterator import FileIterator


class BugzillaBugreport(ABug):
  def __init__(self,textlines,historytextlines,bugid):
    if hasattr(ABug, '__init__'):
      ABug.__init__(self)
    self.lines = textlines
    self.historylines = historytextlines
    self.addAttribute("bugid",bugid)
    self.namedict = {}
    self.namedict["Blocks"] = 'blocks'
    self.namedict["Summary"] = "shortdesc"
    self.namedict['Priority'] = 'priority'
    self.namedict['Status'] = 'status'
    self.namedict['Assignee'] = 'assigned'
    self.namedict['CC'] = 'cc'  
    self.namedict['Component'] = 'component'
    self.namedict['TargetMilestone'] = 'targetmilestone'
    self.namedict['Product'] = 'product'
    self.namedict['Resolution'] ='resolution'
    self.namedict['OS'] = 'os'
    self.namedict['Severity'] = 'severity'
    self.namedict['Dependson'] = 'blocked-by'
    self.namedict['Keywords'] = 'keywords'
    self.namedict['Attachment'] = 'attachment'
    self.namedict['Version'] = 'version'
    self.namedict['Hardware'] = 'hardware'
    self.namedict['Everconfirmed'] = 'Everconfirmed'
    self.namedict['URL'] = 'URL'
    self.namedict['QAContact'] = 'qacontact'
    self.namedict['Whiteboard'] = 'whiteboard'
    self.namedict['Flag'] = 'Flag'
 
  def readChange(self,lines,i,cwho,cwhen):
    if 'attachment.cgi?id=' in lines[i]:
      if 'Flag' in lines[i+2]:
        cwhat = self.namedict["Attachment"] + " - " + "flag" + " - " + lines[i].split('"')[1].replace("\n","")
        crem = ""
        cadd = lines[i+6].split('>')[1].replace("\n","")
      elif 'mime type' in lines[i+2]:
        cwhat = self.namedict["Attachment"] + " - " + "mimetype" + " - " + lines[i].split('"')[1].replace("\n","")
        crem = lines[i+4].split('>')[1]
        cadd = lines[i+6].split('>')[1]
      elif 'description' in lines[i+2]:
        cwhat = self.namedict["Attachment"] + " - " + "description" + " - " + lines[i].split('"')[1].replace("\n","")
        crem = lines[i+4].replace("<td>",'').replace('\n','')
        j = i+5
        while '</td>' in lines[j]:
          crem += '\n' + lines[j].replace("<td>",'').replace('\n','')
          j += 1
        cadd = lines[j+6].replace("<td>",'')
        while '</td>' in lines[j]:
          cadd += '\n' + lines[j].replace("<td>",'').replace('\n','')
          j += 1
        i += j-(i+6)
      elif 'filename' in lines[i+2]:
        cwhat = self.namedict["Attachment"] + " - " + "description" + " - " + lines[i].split('"')[1].replace("\n","")
        crem = lines[i+4].split('>')[1].replace("\n","")
        cadd = lines[i+6].split('>')[1].replace("\n","")
      else:
        crem  = lines[i].split('"')[1].replace("\n","")
        cadd = ""
        cwhat = self.namedict[lines[i+2].split(" is")[0].replace(" ","").replace("\n","")]
      i += 2
    else:
      cwhat = self.namedict[lines[i].replace(" ","").replace("\n","")]
      crem  = lines[i+2].split('>')[1].replace("\n","")
      if 'blocks' == cwhat:
        if len(lines[i+4].split('id=')) > 1:
          cadd = lines[i+4].split('id=')[1].split('"')[0].replace("\n","")
        else:
          cadd = ""
          crem = lines[i+2].split('id=')[1].split('"')[0].replace("\n","")
      else:
        cadd  = lines[i+4].split('>')[1].replace("\n","")
    self.addChange( (cwhat,cadd,crem,cwho,cwhen) )
    return i

  def readChanges(self):
    lines = self.historylines
    cwho  = None
    cwhen = None
    cwhat = None
    crem  = None
    cadd  = None
    i = 0
    while i < len(lines):
      if '<td rowspan="' in lines[i]:
        cwho  = lines[i].split('>')[1].replace("\n","")
        cwhen = lines[i+2].split('>')[1].replace("\n","")
        if int(lines[i].split('"')[1]) > 1:
          i += 3
          while not ( ' </tr>' in lines[i+1] or ' </tr>' in lines[i+2]):
            i += 2
            i = self.readChange(lines,i,cwho,cwhen)
            i += 5
        else:
          i += 5
          i = self.readChange(lines,i,cwho,cwhen)
          i += 3
      i += 1
 
  def readComment(self,i,lines):
    if '<span class="bz_comment_user">' in lines[i] and not 'Description' in lines[i-3]:
      date = string.strip(lines[i+8].replace("\n",""))
      commenter = lines[i].replace('<span class="fn">',"").split('>')[2].split('<')[0]
      comment = []
      j = i + 14
      while not "</div>" in lines[j]:
        comment.append(lines[j].replace("\n",""))
        j+=1
      self.addComment((date,commenter,comment))
    
  def readAttachments(self,i,lines):
    if 'attachment.cgi?id=' in lines[i] and not '&gt;' in lines[i] and not 'bz_comment' in lines[i+2] and not 'bz_comment_text' in lines[i] and not 'Diff' in lines[i] and not 'Details' in lines[i] and not 'Add an attachment' in lines[i]:
      try:
        cfile = string.strip(lines[i+5].replace('\n','')) + " " + string.strip(lines[i+6].replace('\n',''))
        cdesc = ""
        clink = lines[i].split('"')[3]
        cdev = None
        try:
          cdev  = lines[i+11].split('>')[2].split('<')[0]
        except:
          cdev = string.split(lines[i+11].split('>')[1])
        cdate = lines[i+10].split('>')[1].split('<')[0]
        self.addAttachment( (cfile,cdesc,clink,cdev,cdate) )
      except:
        pass
  
  def readCreator(self,i,lines):
    if '<b>Reported</b>' in lines[i]:
      if len(lines[i+2].split('>')) > 3:
        self.addAttribute("creator"     , lines[i+2].split('>')[3].split('<')[0])
      else:
        self.addAttribute("creator"     , lines[i+2].split('>')[2].replace("\n",""))
      self.addAttribute("creationDate", string.strip(lines[i+2].split('>')[1].split('<')[0].replace('by','')))

  def readAssigned(self,i,lines):
    if 'page.cgi?id=fields.html#assigned_to' in lines[i]:
      if len(lines[i+2].split('>')) > 3:
        self.addAttribute("assigned", lines[i+2].split('>')[3].split('<')[0])
      else:
        self.printl(lines,i-2,i+4)
        self.addAttribute("assigned", lines[i+2].split('>')[2].split('<')[0])

  def readCCs(self,i,lines):
    if '<b>CC List</b>' in lines[i]:
      text = None
      j = i+10
      while 'option' in lines[j]:
        if text == None:
          text = lines[j].split('"')[1].replace('\r','').replace('\n','')
        else:
          text += '\n' + lines[j].split('"')[1].replace('\r','').replace('\n','')
        j += 1    
      if text == None:
        text = ''
      self.addAttribute('cc',text)

  def readStatus(self,i,lines):
    if '<span id="static_bug_status">' in lines[i]:
      self.addAttribute("resolution",lines[i+1].replace(" ","").replace('\n',''))
      self.addAttribute("status",lines[i].split('>')[1].replace("\n",""))

  def readProduct(self,i,lines):
    if '"field_container_product"' in lines[i]:
      self.addAttribute("product",lines[i].split('>')[1].split('<')[0]) 

  def readComponent(self,i,lines):
    if '<label for="component"' in lines[i]:
      self.addAttribute("component",string.strip(lines[i+5].split("<td>")[1].replace("\n","")))

  def readVersion(self,i,lines):
    if '<label for="version"><' in lines[i]:
      self.addAttribute("version",lines[i+2].split('>')[1].replace("\n",""))

  def readPlatform(self,i,lines):
    if '<label for="rep_platform"' in lines[i]:
      self.addAttribute("hardware",lines[i+2].split('>')[1].replace("\n",""))
      self.addAttribute("os",lines[i+3].replace(" ","").replace('\n',''))

  def readImportance(self,i,lines):
    if '<label for="priority"' in lines[i]:
      self.addAttribute("priority",lines[i+3].split('>')[1].replace("\n",""))
      self.addAttribute("severity",lines[i+4].replace(" ","").replace('\n',''))

  def readTargetMilestone(self,i,lines):
    if 'label for="target_milestone"' in lines[i]:
      self.addAttribute("targetmilestone",lines[i+2].split('<td>')[1].replace("\n",""))

  def readShortdesc(self,i,lines):
    if '<p class="subheader">' in lines[i]:
      self.addAttribute("shortdesc",lines[i].split(">")[1].split("<")[0].replace("\n",""))

  def readLongdesc(self,i,lines):
    if '<span class="bz_comment_user">' in lines[i] and 'Description' in lines[i-3]:
      j = i + 14
      text = None
      while not "</div>" in lines[j]:
        if text == None:
          text = lines[j].replace('\r','').replace('\n','')
        else:
          text += '\n' + lines[j].replace('\r','').replace('\n','')
        j+=1
      if text == None:
        text = ""
      self.addAttribute("longdesc",text)

  def readBlockedBy(self,i,lines):
    if '<span id="dependson_input_area">' in lines[i] and 'id=' in lines[i+2]:
      text = None
      ts = lines[i+2].split("span> <span")
      for t in ts:
        if text == None:
          text = t.split("id=")[1].split('"')[0].replace("\n","")
        else:
          text += '\n' + t.split("id=")[1].split('"')[0].replace("\n","")
      if text == None:
        text = ''
      self.addAttribute("blocked-by",text)

  def readBlocks(self,i,lines):
    if '<span id="blocked_input_area">' in lines[i] and 'id=' in lines[i+2]:
      ts = lines[i+2].split("span> <span")
      text = None
      for t in ts:
        if text == None:
          text = t.split("id=")[1].split('"')[0].replace("\n","")
        else:
          text += '\n' + t.split("id=")[1].split('"')[0].replace("\n","")
      if text == None:
        text = ''
      self.addAttribute("blocks",text)

  def readQAContact(self,i,lines):
    if 'for="qa_contact' in lines[i] and len(lines[i+2].split('<')) > 3:     
      self.addAttribute("qacontact",lines[i+2].split('>')[3].split('<')[0].replace("\n",""))

  def readWhiteboard(self,i,lines):
    if 'for="status_whiteboard' in lines[i] and '<span title="' in lines[i+2]:
      self.addAttribute("whiteboard",lines[i+2].split('"')[1].replace("\n",""))

  def readKeywords(self,i,lines):
    if 'for="keywords"' in lines[i]:
      if len(lines[i+2].split('>')[1]) > 4:
        self.addAttribute("keywords",string.strip(lines[i+2].split('<td colspan="2">')[1].replace("\n","")))

  def printl(self,lines,a,e):
    import sys
    while a < e:
      sys.stderr.write(str(a) + " " + lines[a].replace("\n","") + '\n')
      a += 1 

  def read(self):
    i = 0
    while i < len(self.lines):
      self.readCreator(i,self.lines)
      self.readAssigned(i,self.lines)
      self.readCCs(i,self.lines)
      self.readStatus(i,self.lines)
      self.readProduct(i,self.lines)
      self.readComponent(i,self.lines)
      self.readVersion(i,self.lines)
      self.readPlatform(i,self.lines)
      self.readImportance(i,self.lines)
      self.readTargetMilestone(i,self.lines)
      self.readShortdesc(i,self.lines)
      self.readLongdesc(i,self.lines)
      self.readBlockedBy(i,self.lines)
      self.readBlocks(i,self.lines)
      self.readComment(i,self.lines)
      self.readAttachments(i,self.lines)
      self.readKeywords(i,self.lines)
      self.readWhiteboard(i,self.lines)
      self.readQAContact(i,self.lines)
      i += 1
    self.readChanges()
      
  def completeChanges(self):
    return True
