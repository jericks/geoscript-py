"""
The :mod:`process` module provides geoprocessing functions.
"""
from org.opengis.referencing.crs import CoordinateReferenceSystem
from org.geotools.process import Processors
from org.geotools.feature import NameImpl as Name
from geoscript import core
from geoscript.layer import Layer

class Process(object):
  """
  A runnable geospatial process.

  A process is typically obtained by name:

  >>> p = Process.lookup('gs:Snap')
  >>> p.description
  Snap to the nearest feature
  """

  @staticmethod
  def processes():
    """
    Static method that returns a generator over the list of known process names.
    Each element is returned as a tuple of (prefix, localName).
    """
    for pf in Processors.getProcessFactories():
      for n in pf.getNames():      
        yield (n.namespaceURI, n.localPart)
 
  @staticmethod
  def lookup(name):
    """
    Static method that looks up a process by name. The *name* parameter is 
    specified as a tuple of (prefix, localName):

    >>> p = Process.lookup(('gs', 'Snap'))
    >>> p.description
    Snap to the nearest feature
    
    *name* may also be specified as a colon delimited string:

    >>> p = Process.lookup('gs:Snap')
    >>> p.description
    Snap to the nearest feature
    """
    n = Name(*name) if isinstance(name,(tuple,list)) else Name(*name.split(':'))
    pf = Processors.createProcessFactory(n)
    if pf:
      p = Process(pf.create(n))
      p.name = name
      p.title = pf.getTitle(n)
      p.description = pf.getDescription(n)

      params = pf.getParameterInfo(n)
      p.inputs = _params(params)
      p.outputs = _params(pf.getResultInfo(n, params))

      return p

  def __init__(self, process=None):
    self._process = process

  def run(self, **args):
    """
    Executes the process with set of named inputs. The input argument names are
    specified by the :attr:`inputs` property. The output arguments names are 
    specified by the :attr:`outputs` property. 

    >>> p = Process.lookup('gs:Reproject')

    >>> from geoscript import geom, proj
    >>> l = Layer()
    >>> l.add([geom.Point(-125, 50)])
    >>> r = p.run(features=l, targetCRS=proj.Projection('epsg:3005'))
    >>> [f.geom.round() for f in r['result']]
    [POINT (1071693 554290)]
    """
    # map the inputs to java
    m = {}
    for k,v in args.iteritems(): 
      # special case for layer
      if isinstance(v, Layer):
        v = v.cursor()

      m[k] = core.unmap(v)
    
    # run the process
    result = self._process.execute(m, None)

    # reverse map the outputs back 
    r = {}
    for k, v in dict(result).iteritems():
      r[k] = core.map(v)

    return r

def _params(m):
  d = {}
  for k,v in dict(m).iteritems():
     d[k] = (v.name, core.map(v.type), v.description)
  return d 

