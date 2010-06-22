import os

class FileIterator:
  def __init__(self, directory, filter=None):
    self.directory = directory
    self.filter = filter
    self.directorylist = os.listdir(directory)
    self.index = 0
    
  def hasNext(self):
    if self.index < len(self.directorylist):
      if os.path.isfile(self.directory + "/" + self.directorylist[self.index]):
        if self.filter == None:
          return True
        elif self.filter.check(self.directorylist[self.index],self.directory):
          return True
      self.index += 1
      return self.hasNext()
    return False
    
  def next(self):
    if os.path.isfile(self.directory + "/" + self.directorylist[self.index]):
      if self.filter == None:
        self.index += 1
        return (self.directorylist[self.index - 1])
      elif self.filter.check(self.directorylist[self.index],self.directory):
        self.index += 1
        return (self.directorylist[self.index - 1])
    self.index += 1
    return self.next()
