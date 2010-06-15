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
      return self.directorylist[self.index - 1]
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
    
  def removeNoise(self,line):
    return line.replace("<!-- google_ad_section_start -->","").replace("<!-- google_ad_section_end -->","")
    
  def read(self):
    f = open(self.directory+"/"+self.filename)
    lines = f.readlines()
    f.close()
    i = 0
    while i < len(lines):
      line = lines[i]
      if "Submited:" in line:
        self.attributes["creator"] = self.removeNoise(lines[i+1]).split('<p>')[1].split(' - ')[0]
        self.attributes["creationDate"] = self.removeNoise(lines[i+1]).split('</p>')[0].split(' - ')[1]
      if "Status:" in line:
        self.attributes["status"] = self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0]
      if "<label>Resolution:</label>" in line:
        self.attributes["resolution"] = self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0]
      if "Assigned:" in line:
        self.attributes["assigned"] = self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0]
      if "Category:" in line:
        self.attributes["category"] = self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0]
      if "Group:" in line:
        self.attributes["group"] = self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0]
      if "Visibility:" in line:
        self.attributes["visibility"] = self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0]
      if "Priority:" in line:
        self.attributes["priority"] = self.removeNoise(lines[i+1]).split('<p>')[1].split('</p>')[0]
      if "Details:" in line:
        j = i+1
        self.attributes["longdesc"] = []
        while not '<hr noshade="noshade" class="divider" />' in lines[j]:
          self.attributes["longdesc"].append(self.removeNoise(lines[j]))
          j += 1
      if (" - ID: " + self.attributes["bugid"]) in line:
        self.attributes["shortdesc"] = self.removeNoise(lines[i]).split('<strong>')[1].split('</strong>')[0]
      if '<h4 class="titlebar toggle" id="filebar">Attached File' in line and not 'No Files Currently Attached' in lines[i+2]:
        j = i + 12
        print lines[j]
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
              self.attachments.append((cfile,cdesc,self.removeNoise(lines[j])))
              cfile = None
              cdesc = None
          j += 1
      if '<tr class="artifact_comment " id="artifact_comment_"' in line:
        date = lines[i+6].split(": ")[1].split("<br")[0]
        commenter = lines[i+7].split(": ")[1]
        comment = []
        j = i + 12
        while not "</div>" in lines[j]:
          comment.append(lines[j])
          j+=1
        self.comments.append((date,commenter,comment))
      if '<h4 class="titlebar toggle" id="changebar">Change' in line and not "No changes have been made to this artifact." in lines[i+2]:
        j = i + 15
        cfield    = None
        cvalue    = None
        cmodifier = None
        cdate     = None
        while not "</tbody>" in lines[j]:
          if not "<tr" in lines[j] and not "</tr>" in lines[j] and not "<td" in lines[j] and not "</td>" in lines[j] and len(lines[j])>1:
            if cfield == None:
              cfield = lines[j]
            elif cvalue == None:
              cvalue = lines[j]
            elif cmodifier == None:
              cmodifier = lines[j]
            else:
              cdate = lines[j]
              self.changes.append((cfield,cvalue,cmodifier,cdate))
              cfield = None
              cvalue = None
              cmodifier = None
              cdate = None
          j += 1
      i += 1
    
  def attribute2xml(self,attribute,indentation):
    s = indentation
    print s+"<attribute>"
    print s+"  <name>"
    print s+"    "+attribute[0]
    print s+"  </name>"
    print s+"  <value>"
    if type(attribute[1]) == type([]):
      for l in attribute[1]:
        print l
    else:
      print s+"    "+attribute[1]
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
    print s+"    "+comment[1]
    print s+"  </commenter>"
    print s+"  <date>"
    print s+"    "+comment[0]
    print s+"  </date>"
    print s+"  <comment>"
    for l in comment[2]:
      print l
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
    print s+"    "+change[0]
    print s+"  </name>"
    print s+"  <old-value>"
    print s+"    "+change[1]
    print s+"  </old-value>"
    print s+"  <modifier>"
    print s+"    "+change[2]
    print s+"  </modifier>"
    print s+"  <modify-date>"
    print s+"    "+change[3]
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
    print s+"  "+attachment[0]
    print s+"  </filename>"
    print s+"  <description>"
    print s+"  "+attachment[1]
    print s+"  <description/>"
    print s+"  <link>"
    print s+"  "+attachment[2]
    print s+"  </link>"
    print s+"</attachment>"
    
  def attachments2xml(self,indentation):
    s = indentation
    print s+"<attachments>"
    for attachment in self.attachments:
      self.attachment2xml(attachment,indentation+"  ")
    print s+"</attachments>"
    print "toImplement"
    
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
    b.toXML("  ")
  print "</bugs>" 
