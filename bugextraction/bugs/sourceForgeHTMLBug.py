from ABug import ABug

class SourceForgeBugreport(ABug):
  def __init__(self,textlines,bugid):
    if hasattr(ABug, '__init__'):
      ABug.__init__(self)
    self.lines = textlines
    self.addAttribute("bugid",bugid)
    self.namedict = {}
    self.noChange = []
    self.namedict['status_id'] = "status"
    self.namedict['resolution_id'] = "resolution"
    self.namedict['close_date'] = "close-date"
    self.noChange.append('close-date')  
    self.namedict['FileAdded'] = 'FileAdded'
    self.noChange.append('FileAdded')
    self.namedict['assigned_to'] = 'assigned'
    self.namedict['priority'] = 'priority'
    self.namedict['category_id'] = 'category'
    self.namedict['artifact_group_id'] = 'group'
    self.namedict['allow_comments'] = 'allow_comments'
    self.noChange.append('allow_comments')
    self.namedict['FileDeleted'] = 'FileDeleted'
    self.noChange.append('FileDeleted')

  def removeNoise(self,line):
    return line.replace("<!-- google_ad_section_start -->","").replace("<!-- google_ad_section_end -->","")

  def readCreation(self,i,lines):
    if "Submited:" in lines[i]:
      self.addAttribute("creator", self.removeNoise(lines[i+1]).split('<p>')[1].split(' - ')[0])
      self.addAttribute("creationDate", self.removeNoise(lines[i+1]).split('</p>')[0].split(' - ')[1])
    
  def readStatus(self,i,lines):
    if "Status:" in lines[i]:        
      self.addAttribute("status", self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0])
  
  def readResolution(self,i,lines):
    if "<label>Resolution:</label>" in lines[i]:        
      self.addAttribute("resolution", self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0])

  def readAssigned(self,i,lines):
    if "Assigned:" in lines[i]:
      self.addAttribute("assigned", self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0])

  def readCategory(self,i,lines):
    if "Category:" in lines[i]:
      self.addAttribute("category", self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0])

  def readGroup(self,i,lines):
    if "Group:" in lines[i]:
      self.addAttribute("group", self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0])

  def readVisibility(self,i,lines):
    if "Visibility:" in lines[i]:
      self.addAttribute("visibility", self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0])

  def readPriority(self,i,lines):
    if "Priority:" in lines[i]:
      self.addAttribute("priority", self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0])

  def readDetails(self,i,lines):
    if "Details:" in lines[i]:        
      j = i+1
      self.addAttribute("longdesc", [])
      while not '<hr noshade="noshade" class="divider" />' in lines[j]:
        self.addAttribute("longdesc", self.removeNoise(lines[j]))
        j += 1
   
  def readShortdesc(self,i,lines):
    if (" - ID: " + self.attributes["bugid"]) in lines[i]:
      self.addAttribute("shortdesc", self.removeNoise(lines[i]).split('<strong>')[1].split('</strong>')[0])

  def readAttachments(self,i,lines):
    if '<h4 class="titlebar toggle" id="filebar">Attached File' in lines[i] and not 'No Files Currently Attached' in lines[i+2]:
      j = i + 12
      cfile = None
      cdesc = None
      clink = None
      while not "</table>" in lines[j]:
        if not "<tr" in lines[j] and not "</tr>" in lines[j] and not "<td" in lines[j] and not "</td>" in lines[j] and len(lines[j])>1:
          if cfile == None:
            cfile = self.removeNoise(lines[j])
          if cdesc == None:
            cdesc = self.removeNoise(lines[j])
          if clink == None:
            self.addAttachment((cfile,cdesc,self.removeNoise(lines[j])))
            cfile = None
            cdesc = None
        j += 1    

  def readComment(self,i,lines):
    if '<tr class="artifact_comment " id="artifact_comment_"' in lines[i]:
      date = lines[i+6].split(": ")[1].split("<br")[0]
      commenter = lines[i+7].split(": ")[1]
      comment = []
      j = i + 12
      while not "</div>" in lines[j]:
        comment.append(lines[j])
        j+=1
      self.addComment((date,commenter,comment))

  def readChanges(self,i,lines):
    if '<h4 class="titlebar toggle" id="changebar">Change' in lines[i] and not "No changes have been made to this artifact." in lines[i+2]:
      j = i + 15
      cfield    = None
      cvalue    = None
      cmodifier = None
      cdate     = None
      while not "</tbody>" in lines[j]:
        if not "<tr" in lines[j] and not "</tr>" in lines[j] and not "<td" in lines[j] and not "</td>" in lines[j] and len(lines[j])>1:
          if cfield == None:
            cfield = self.namedict[lines[j].replace(" ","").replace("\n","")]
          elif cvalue == None:
            cvalue = lines[j]
          elif cmodifier == None:
            cmodifier = lines[j]
          else:
            cdate = lines[j]
            if not cfield in self.noChange:
              self.addChange((cfield,None,cvalue,cmodifier,cdate))
            cfield = None
            cvalue = None
            cmodifier = None
            cdate = None
        j += 1
    i += 1

  def read(self):
    lines = self.lines
    i = 0
    while i < len(lines):
      self.readCreation(i,lines)
      self.readStatus(i,lines)
      self.readResolution(i,lines)
      self.readAssigned(i,lines)
      self.readCategory(i,lines)
      self.readGroup(i,lines)
      self.readVisibility(i,lines)
      self.readPriority(i,lines)
      self.readDetails(i,lines)
      self.readShortdesc(i,lines)
      self.readAttachments(i,lines)
      self.readComment(i,lines)
      self.readChanges(i,lines)
      i += 1
      
  def completeChanges(self):
    c = {}
    for k in self.attributes.keys():
      c[k] = self.attributes[k]
    i = 0
    while i < len(self.changes):
      change = self.changes[i]
      t = change[2]
      if change[0] == 'close-date':
        self.changes[i] = (change[0],"---",change[2],change[3],change[4])
      else:
        self.changes[i] = (change[0],c[change[0]],change[2],change[3],change[4])
      c[change[0]] = t
      i += 1 
