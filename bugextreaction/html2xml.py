import sys
import getopt
import os

from bugs.chromeHTMLBug      import ChromeBugreport
from bugs.sourceForgeHTMLBug import SourceForgeBugreport
from bugs.bugzillaHTMLBug    import BugzillaBugreport

from util.FileIterator       import FileIterator
from util.AFilter            import AFilter


def usage():
  sys.stderr.write(sys.argv[0] + " -d/--directory directory -c/--chrome -s/--sourceforge -b/--bugzilla\n")

def bugzilla(directory):
  class NoHistory(AFilter):
    def check(self,filename,directory):
      return not 'history' in filename
  fi = FileIterator(direcotry,NoHistory())
  while fi.hasNext():
    fn = fi.next()
    f.open(directory+"/"+fn)
    lines = f.readlines()
    f.close()
    f.open(directory+"/"+fn.replace(".""-history."))
    hlines = f.readlines()
    f.close()
    b = BugzillaBugreport(lines,hlines,fn.split('.')[0])

def chrome(directory):
  fi = FileIterator(directory)
  while fi.hasNext():
    fn = fi.next()
    f = open(directory+"/"+fn)
    lines = f.readlines()
    f.close()
    b = ChromeBugreport(lines,fn.split(".")[0])
    b.read()
    if b.attributes.has_key("shortdesc"):
      b.completeChanges()
      b.toXML("  ")
    else:
      sys.stderr.write("the bug report "+b.attributes["bugid"]+" couldn't be parsed correctly\n")

def sourceforge(directory):
  fi = FileIterator(directory)
  while fi.hasNext():
    fn = fi.next()
    f = open(directory+"/"+fn)
    lines = f.readlines()
    f.close()
    b = SourceForgeBugreport(lines,fn.split(".")[0])
    b.read()
    if b.attributes.has_key("shortdesc"):
      b.completeChanges()
      b.toXML("  ")
    else:
      sys.stderr.write("the bug report "+b.attributes["bugid"]+" couldn't be parsed correctly\n")

directory = None

if __name__=="__main__":
  arguments = sys.argv[1:]
  optlist, args = getopt.getopt(arguments, 'd:csb',["directory=","chrome","sourceforge","bugzilla"])
  bugtype = None
  for o, a in optlist:
    if o in ['-d','--directory']:
      directory = a
    if o in ['-c','--chrome']:
      if bugtype != None:
        sys.stderr.write("only one bug type pretty please with a cherry on top ^^\n")
        sys.exit(-1)
      bugtype = chrome
    if o in ['-s','--sourceforge']:
      if bugtype != None:
        sys.stderr.write("only one bug type pretty please with a cherry on top ^^\n")
        sys.exit(-1)
      bugtype = sourceforge
    if o in ['-b','--bugzilla']:
      if bugtype != None:
        sys.stderr.write("only one bug type pretty please with a cherry on top ^^\n")
        sys.exit(-1)
      bugtype = bugzilla
  if directory == None or bugtype == None:
    print "hello"
    usage()
    sys.exit(-1)
  print "<bugs>"
  bugtype(directory)
  print "</bugs>" 
