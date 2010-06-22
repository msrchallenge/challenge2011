import urllib

def retryFetchPage(url,delay=0):
  try:
    sock = urllib.urlopen(url)
    source = sock.read()
    sock.close()
    return source
  except Exception:
    time.sleep(delay)
    return retryFetchPage(url,delay+1)
