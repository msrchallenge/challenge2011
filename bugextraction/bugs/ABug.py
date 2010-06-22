#
#
#

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
    print s+"  <new-value>"
    print s+"    "+change[1]
    print s+"  </new-value>"
    print s+"  <old-value>"
    print s+"    "+change[2]
    print s+"  </old-value>"
    print s+"  <modifier>"
    print s+"    "+change[3]
    print s+"  </modifier>"
    print s+"  <modify-date>"
    print s+"    "+change[4]
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
    
  def toXML(self,indentation):
    s = indentation
    print s+"<bug>"
    self.attributes2xml(indentation+"  ")
    self.comments2xml(indentation+"  ")
    self.changes2xml(indentation+"  ")
    self.attachments2xml(indentation+"  ")
    print s+"</bug>"
    
