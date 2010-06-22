class AFilter:
  def check(self,filename,directory):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError('AFilter.check(filename,directory) must be implemented in subclass')
    