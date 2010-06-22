import urllib
import time

def retryFetchPage(url,delay=0):
  try:
    sock = urllib.urlopen(url)
    source = sock.read()
    sock.close()
    return source
  except Exception:
    time.sleep(delay)
    return retryFetchPage(url,delay+1)


class ABugIterator:
  def hasNext(self):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('ABug.read() must be implemented in subclass')
 
  def next(self):
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
      return retryFetchPage(url,delay+1)

