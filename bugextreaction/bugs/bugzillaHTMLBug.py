from ABug import ABug
from .util.FileIterator import FileIterator


class BugzillaBugreport(ABug):
  def __init__(self,textlines,bugid):
    if hasattr(ABug, '__init__'):
      ABug.__init__(self)
    self.lines = textlines
    self.addAttribute("bugid",bugid)
    self.namedict = {}
    
  def readChanges(self,j,lines):
    print "to implement"
 
  def readComment(self,i,lines):
    if '<span class="bz_comment_user">' in lines[i] and not 'Description' in lines[i-3]:
      date = lines[i+8]
      commenter = lines[i].split('>')[3].split('<')[0]
      comment = []
      j = i + 14
      while not "</div>" in lines[j]:
        comment.append(lines[j])
        j+=1
      self.addComment((date,commenter,comment))
      self.readChanges(j,lines)
    
  def readAttachments(self,i,lines):
    if 'attachment.cgi?id=' in lines[i] and not 'Details' in lines[i]:
      cfile = lines[i+5] + " " + lines[i+6].repalce(" ","")
      cdesc = ""
      clink = lines[i].split('"')[4]
      cdev  = lines[i+11].split('>')[2].split('<')[0]
      cdate = lines[i+10].split('>')[1].split('<')[0]
      self.addAttachment( (cfile,cdesc,clink,cdev,cdate) )
    
  def readCreator(self,i,lines):
    if '<b>Reported</b>' in lines[i]:
      self.addAttribute("creator"     , lines[i+2].split('>')[3].split('<')[0])
      self.addAttribute("creationDate", lines[i+2].split('>')[1].split('<')[0].replace('by',''))

  def readAssigned(self,i,lines):
    if 'Assigned To' in lines[i]:
      self.addAttribute("assigned", lines[i+2].split('>')[3].split('<')[0])

  def readCCs(self,i,lines):
    if '<b>CC List</b>' in lines[i]:
      self.addAttribute("cc",[])
      j = i+10
      while not 'option' in lines[j]:
        self.addAttribute("cc",lines[j].split('"')[1])
        j += 1    

  def readStatus(self,i,lines):
    if '<span id="static_bug_status">' in lines[i]:
      self.addAttribute("status",lines[i].split('>')[1]+" "+lines[i+1].replace(" ",""))

  def readProduct(self,i,lines):
    if '"field_container_product"' in lines[i]:
      self.addAttribute("product",lines[i].split('>')[1].split('<')) 

  def readComponent(self,i,lines):
    if '<label for="component"' in lines[i]:
      self.addAttribute("component",lines[i+5].split(">")[1])

  def readVersion(self,i,lines):
    if '<label for="version"><' in lines[i]:
      self.addAttribute("version",lines[i+2].split('>'))

  def readPlatform(self,i,lines):
    if '<label for="rep_platform"' in lines[i]:
      self.addAttribute("platform",lines[i+2].split('>')+" "+lines[i+3].replace(" ",""))

  def readImportance(self,i,lines):
    if '<label for="priority"' in lines[i]:
      self.addAttribute("importance",lines[i+3].split('>')[1]+" "+lines[i+4].replace(" ",""))

  def readTargetMilestone(self,i,lines):
    if 'label for="target_milestone"' in lines[i]:
      self.addAttribute("targetmilestone",lines[i+2].split('>'))

  def readShortdesc(self,i,lines):
    if '<p class="subheader">' in lines[i]:
      self.addAttribute("shortdesc",lines[i].split(">")[1].split("<")[0])

  def readLongdesc(self,i,lines):
    if '<span class="bz_comment_user">' in lines[i] and 'Description' in lines[i-3]:
      comment = []
      j = i + 14
      while not "</div>" in lines[j]:
        comment.append(lines[j])
        j+=1
      self.addAttribute("longdesc",comment)

  def readBlockedBy(self,i,lines):
    if '<span id="dependson_input_area">' in lines[i] and len(lines[i+2]) > 6:
      j = i+2
      self.addAttribute("blocked-by",[])
      while not '</td>' in lines[j]:
        self.addAttribute("blocked-by",lines[j].split('id=')[1].split('"')[0])
        j += 1

  def readBlocks(self,i,lines):
    if '<span id="blocked_input_area">' in lines[i] and len(lines[i+2]) > 6:
      j = i+2
      self.addAttribute("blocks",[])
      while not '</td>' in lines[j]:
        self.addAttribute("blocks",lines[j].split('id=')[1].split('"')[0])
        j += 1

  def readQAContact(self,i,lines):
    if 'for="qa_contact' in lines[i]:
      print "need to implement"

  def readWhiteboard(self,i,lines):
    if 'for="status_whiteboard' in lines[i]:
      print "need to implement"

  def readKeywords(self,i,lines):
    if 'for="keywords"' in lines[i]:
      print "need to implement"

  def read(self):
    print "need to update"
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
    print "need to implement"
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
