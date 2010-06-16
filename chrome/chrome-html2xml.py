import sys
import getopt
import os


class FileIterator:
  def __init__(self, directory):
    self.directory = directory
    self.directorylist = os.listdir(directory)  
    self.index = 0
    
  def hasNext(self):
    if self.index < len(self.directorylist):
      if os.path.isfile(self.directory + "/" + self.directorylist[self.index]):
        return True
      self.index += 1
      return self.hasNext()
    return False
    
  def next(self):
    if os.path.isfile(self.directory + "/" + self.directorylist[self.index]):
      self.index += 1
      return (self.directorylist[self.index - 1])
    self.index += 1
    return self.next()



class bugreport:
  def __init__(self,filename,directory):
    self.filename = filename
    self.directory = directory
    self.attributes = {}
    self.attributes["bugid"] = filename.split(".")[0]
    self.comments = []
    self.changes = []
    self.attachments = []
    self.namedict = {}
    self.namedict['Summary'] = 'shortdesc'
    self.namedict['Status'] = 'status'
    self.namedict['Labels'] = 'label'
    self.namedict['Owner'] = 'assigned'
    self.namedict['Cc'] = 'cc'
    self.namedict['Mergedinto'] = 'merge'
    self.namedict['Blockedon'] = 'blocked-by'
    self.namedict['Blocks'] = 'blocks'
    
  def read(self):
    f = open(self.directory+"/"+self.filename)
    lines = f.readlines()
    f.close()
    i = 0
    while i < len(lines):
      line = lines[i]
      if '<div class="author">' in line:
        self.attributes["creator"] = lines[i+1].replace("Reported by ","")
        self.attributes["creationDate"] = lines[i+1].split('"')[3]
      if '<tr><th align="left">Owner:&nbsp;</th><td>' in line:
        self.attributes["assigned"] = lines[i+2]
      if '<a href="list?q=label:' in line and not '<tr><td colspan="2">' in line:
        if not self.attributes.has_key("label"):
          self.attributes["label"] = []
        self.attributes["label"].append(lines[i].split('"')[1].split(":")[1] + lines[i+1].split('"')[1])
      if '<tr><th class="vt" align="left">Cc:&nbsp;</th><td>' in line:
        if not self.attributes.has_key("cc"):
          self.attributes["cc"] = []
        j = i+3
        while not "</td>" in lines[j]:
          for cc in lines[j].split(",  "):
            self.attributes["cc"].append(cc)
          j += 1
      if '<tr><th align="left">Status:&nbsp;</th>' in line:
        self.attributes["status"] = ""
#        sys.stderr.write(self.filename+" , "+lines[i+3]+" , "+str(i+3)+" , "+str(len(lines[i+3])))
        if len(lines[i+3]) > 4:
          self.attributes["status"] = lines[i+3].split(">")[1] + " -- " + lines[i+3].split('"')[1]
      if 'Issue <a href="detail?id=' in line:
        self.attributes["shortdesc"] = lines[i+3].split(">")[1].split("<")[0]
      if '<td class="vt issuedescription" width="100%">' in line:
        j = i+7
        self.attributes["longdesc"] = []
        while not '</pre>' in lines[j]:
          self.attributes["longdesc"].append(lines[j])
          j += 1
      if '<br><b>Blocked on:</b><br>' in line:
        j = i+7
        if not self.attributes.has_key('blocked-by'):
          self.attributes['blocked-by'] = []
        while not '</div>' in lines[j]:
          if 'issue' in lines[j]:
            self.attributes['blocked-by'].append(lines[j].split(' ')[1].split('<')[0])
          j+=1
      if '<br><b>Blocking:</b><br>' in line:
        j = i
        if not self.attributes.has_key('blocks'):
          self.attributes['blocks'] = []
        while not '</div>' in lines[j]:
          if 'issue' in lines[j]:
            self.attributes['blocks'].append(lines[j].split(' ')[1].split('<')[0])
          j += 1
          
      if '<span class="author">Comment <a name=' in line:
        date = lines[i+4].split('"')[3]
        commenter = lines[i+3]
        comment = []
        j = i + 7
        while not "</pre>" in lines[j]:
          comment.append(lines[j])
          j+=1
        self.comments.append((date,commenter,comment))
        # starting changes here
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
                    self.changes.append((cfield,nvalue,ovalue,commenter,date))  
              elif cfield == "merge":
                ovalue = change.split('</b> ')[1]
                self.changes.append((cfield,ovalue,ovalue,commenter,date))
              else:
                nvalue = None
                ovalue = change.split('</b> ')[1]
                self.changes.append((cfield,nvalue,ovalue,commenter,date))
      if '<div class="attachments">' in line:
        j = i + 12
        cfile = None
        cdesc = None
        clink = None
        while not "</div>" in lines[j]:
          if '<table' in line:
            cfile = lines[j+8].split('>')[1].split('<')[0]
            cdesc = ""
            clink = lines[j+15].split('"')[1].replace("amp&","")
            self.attachments.append( (cfile,cdesc,clink) )
          j += 1
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
        self.changes[i] = (change[0],c[change[0]],change[2],change[3])
        c[change[0]] = t
      i += 1
    
  def attribute2xml(self,attribute,indentation):
    s = indentation
    print s+"<attribute>"
    print s+"  <name>"
    print s+"    "+attribute[0].replace('\n','')
    print s+"  </name>"
    print s+"  <value>"
    if type(attribute[1]) == type([]):
      for l in attribute[1]:
        print l.replace('\n','')
    else:
      print s+"    "+attribute[1].replace('\n','')
    print s+"  </value>"
    print s+"</attribute>"
    
  def attributes2xml(self,indentation):
    s = indentation
    print s+"<attributes>"
    for key in self.attributes.keys():
      self.attribute2xml((key,self.attributes[key]),indentation+"  ")
    print s+"</atributes>"
    
  def comment2xml(self,comment,indentation):
    s = indentation
    print s+"<comment>"
    print s+"  <commenter>"
    print s+"    "+comment[1].replace('\n','')
    print s+"  </commenter>"
    print s+"  <date>"
    print s+"    "+comment[0].replace('\n','')
    print s+"  </date>"
    print s+"  <comment>"
    for l in comment[2]:
      print l.replace('\n','')
    print s+"  </comment>"
    print s+"</comment>"
    
  def comments2xml(self,indentation):
    s = indentation
    print s+"<comments>"
    for comment in self.comments:
      self.comment2xml(comment,indentation+"  ")
    print s+"</comments>"
    
  def change2xml(self,change,indentation):
    s = indentation
    print s+"<change>"
    print s+"  <name>"
    print s+"    "+change[0].replace('\n','')
    print s+"  </name>"
    print s+"  <old-value>"
    print s+"    "+change[1].replace('\n','')
    print s+"  </old-value>"
    print s+"  <modifier>"
    print s+"    "+change[2].replace('\n','')
    print s+"  </modifier>"
    print s+"  <modify-date>"
    print s+"    "+change[3].replace('\n','')
    print s+"  </modify-date>"
    print s+"</change>"
    
  def changes2xml(self,indentation):
    s = indentation
    print s+"<changes>"
    for change in self.changes:
      self.change2xml(change,indentation+"  ")
    print s+"</changes>"
    
  def attachment2xml(self,attachment,indentation):
    s = indentation
    print s+"<attachment>"
    print s+"  <filename>"
    print s+"  "+attachment[0].replace('\n','')
    print s+"  </filename>"
    print s+"  <description>"
    print s+"  "+attachment[1].replace('\n','')
    print s+"  <description/>"
    print s+"  <link>"
    print s+"  "+attachment[2].replace('\n','')
    print s+"  </link>"
    print s+"</attachment>"
    
  def attachments2xml(self,indentation):
    s = indentation
    print s+"<attachments>"
    for attachment in self.attachments:
      self.attachment2xml(attachment,indentation+"  ")
    print s+"</attachments>"
    
  def toXML(self,indentation):
    s = indentation
    print s+"<bug>"
    self.attributes2xml(indentation+"  ")
    self.comments2xml(indentation+"  ")
    self.changes2xml(indentation+"  ")
    self.attachments2xml(indentation+"  ")
    print s+"</bug>"
      

#b = bugreport('2799592.html','.')
#b.read()



def usage():
  sys.stderr.write(sys.argv[0] + " -d directory\n")

directory = None

if __name__=="__main__":
  arguments = sys.argv[1:]
  optlist, args = getopt.getopt(arguments, 'd:')
  for o, a in optlist:
    if o in ['-d']:
      directory = a
  if directory == None:
    usage()
    sys.exit(-1)
  fi = FileIterator(directory)
  print "<bugs>"
  while fi.hasNext():
    fn = fi.next()
    b = bugreport(fn,directory)
    b.read()
    if b.attributes.has_key("shortdesc"):
      b.completeChanges()
      b.toXML("  ")
  print "</bugs>" 
