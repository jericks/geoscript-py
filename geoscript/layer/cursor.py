from org.geotools.feature import FeatureCollection
from geoscript import core
from geoscript.feature import Feature
from geoscript.filter import Filter

class Cursor(object):
  """
  A cursor or iterator over :class:`Feature <geoscript.feature.feature.Feature>` objects.
  """

  def __init__(self, fcol, layer=None):
    self._fcol = fcol
    self._reader = None
    self.layer = layer

  def next(self):
    if not self._reader:
      self._reader = self._fcol.features()

    """
    Returns the next feature. Raises `StopIteration` if no more features are available.
    """
    if not self._reader.hasNext():
      self._reader.close()
      raise StopIteration

    return Feature(schema=self.layer.schema if self.layer else None, f=self._reader.next())
  
  def read(self, n):
    """
    Reads n features into a `list`. If less than n features are available the resulting list will have a size less than n.

    *n* is the number of features to read.
    """
    features = [] 
    for i in range(n):
      try:
        features.append(self.next())
      except StopIteration:
        break

    return features

  def close(self):
    """
    Closes the cursor. This function should *always* be called by client code after the cursor is no longer needed or has been exhausted.
    """
    if self._reader:
      self._reader.close()

  def __iter__(self):
    return self

core.registerTypeMapping(FeatureCollection, Cursor)
core.registerTypeUnmapping(Cursor, FeatureCollection, lambda x: x._fcol)
