import sys

class ABug:
  attachments = []
  changes = []
  attributes = {}
  comments = []

  def __init__(self):
    self.attachments = []
    self.changes = []
    self.attributes = {}
    self.comments = []

  def read(self):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('ABug.read() must be implemented in subclass')
  
  def completeChanges(self):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('ABug.completeChanges() must be implemented in subclass')
  
  def addAttachment(self,attachment):
    self.attachments.append(attachment)

  def addToAttribute(self,attribute,value):
    self.attributes[attribute] = self.attributes[attribute] + value
  
  def addChange(self,change):
    self.changes.append(change)
   
  def addAttribute(self,attribute,value):
    if self.attributes.has_key(attribute):
      if type(self.attributes[attribute]) == type([]):
        self.attributes[attribute].append(value)
      else:
        raise "In BugID #"+self.attributes["bugid"]+" already has attribute: " + attribute + " with value: " + value
    else:
      self.attributes[attribute] = value
  
  def addComment(self,comment):
    self.comments.append(comment)
  
  def attribute2xml(self,attribute,indentation):
    s = indentation
    print s+"<attribute>"
    sys.stdout.write(s+"  <name>" + attribute[0])
    sys.stdout.write("</name>\n")
    sys.stdout.write(s+"  <value>" + attribute[1])
    sys.stdout.write("</value>\n")
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
    sys.stdout.write(s+"  <commenter>")
    sys.stdout.write(comment[1])
    sys.stdout.write("</commenter>\n")
    sys.stdout.write(s+"  <date>")
    sys.stdout.write(comment[0])
    sys.stdout.write("</date>\n")
    sys.stdout.write(s+"  <comment>")
    for l in comment[2]:
      print l.replace('\n','')
    sys.stdout.write("</comment>\n")
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
    sys.stdout.write(s+"  <name>")
    sys.stdout.write(change[0])
    sys.stdout.write("</name>\n")
    sys.stdout.write(s+"  <new-value>")
    sys.stdout.write(change[1])
    sys.stdout.write("</new-value>\n")
    sys.stdout.write(s+"  <old-value>")
    sys.stdout.write(change[2])
    sys.stdout.write("</old-value>\n")
    sys.stdout.write(s+"  <modifier>")
    sys.stdout.write(change[3])
    sys.stdout.write("</modifier>\n")
    sys.stdout.write(s+"  <modify-date>")
    sys.stdout.write(change[4])
    sys.stdout.write("</modify-date>\n")
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
    sys.stdout.write("  <filename>")
    sys.stdout.write(attachment[0])
    sys.stdout.write("</filename>\n")
    sys.stdout.write(s+"  <description>")
    sys.stdout.write(attachment[1])
    sys.stdout.write("<description/>\n")
    sys.stdout.write(s+"  <link>")
    sys.stdout.write(attachment[2])
    sys.stdout.write("</link>\n")
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
    
