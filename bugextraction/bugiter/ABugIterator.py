import urllib
import time

class ABugIterator:
  def hasNext(self):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('ABug.read() must be implemented in subclass')

  def init(self):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('ABug.read() must be implemented in subclass')

  def next(self):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('ABug.read() must be implemented in subclass')

  def write(self,write,p,downloaddir):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('ABug.read() must be implemented in subclass')

  def retryFetchPage(self,url,delay=0):
    try:
      sock = urllib.urlopen(url)
      source = sock.read()
      sock.close()
      return source
    except Exception:
      time.sleep(delay)
      return self.retryFetchPage(url,delay+1)

