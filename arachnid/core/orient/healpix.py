''' pyHEALPix Library

It works with Euler angles in the ZYZ convention.

.. Created on Aug 17, 2012
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
import logging, numpy


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

try:
    from core._healpix import pix2ang_nest, \
                                  pix2ang_ring, \
                                  ang2pix_nest, ang2pix_ring, ring2nest, nest2ring, nside2npix, npix2nside
    pix2ang_nest, pix2ang_ring, ang2pix_nest, ang2pix_ring, ring2nest, nest2ring, nside2npix, npix2nside;
except:
    from ..app import tracing
    tracing.log_import_error("Failed to import pyHEALPix module - certain functionality will not be available", _logger)

def _ensure_theta(theta, half=False):
    ''' Ensure theta falls in the proper range, 0-180.0
    
    :Parameters:
    
    theta : float
            Theta value
    half : bool, optional
           If true, then assume theta can be mirrored
           
    :Returns:
    
    theta : float
            Theta value in proper range
    '''
    
    if theta >= numpy.pi: 
        if half: theta = theta - numpy.pi
        else: theta = theta - numpy.pi/2
    return theta

def ang2pix(resolution, theta, phi=None, scheme='ring', half=False, out=None):
    ''' Convert Euler angles to pixel
    
    :Parameters:
    
    resolution : int
                 Pixel resolution
    theta : float or array
            Euler angle theta or array of Euler angles
    phi : float
          Euler angle phi or optional if theta is array of both
    scheme : str
             Pixel layout scheme: nest or ring
    half : bool
           Convert Euler angles to half volume
    out : array, optional
          Array of pixels for specified array of Euler angles
    
    :Returns:
    
    out : in or, array
          Pixel for specified Euler angles
    '''
    import healpix
    
    if scheme not in ('nest', 'ring'): raise ValueError, "scheme must be nest or ring"
    if hasattr(theta, '__iter__'):
        if phi is not None and not hasattr(phi, '__iter__'): 
            raise ValueError, "phi must be None or array when theta is an array"
        if hasattr(phi, '__iter__'): theta = zip(theta, phi)
        _ang2pix = getattr(healpix, 'ang2pix_%s'%scheme)
        if out is None: out = numpy.zeros(len(theta), dtype=numpy.long)
        i = 0
        for t, p in theta:
            t = _ensure_theta(t, half)
            out[i] = _ang2pix(int(resolution), float(t), float(p))
            i += 1
        return out
    else:
        _ang2pix = getattr(healpix, 'ang2pix_%s'%scheme)
        if phi is None: "phi must not be None when theta is a float"
        theta = _ensure_theta(theta, half)
        return _ang2pix(int(resolution), float(theta), float(phi))

def coarse(resolution, theta, phi=None, scheme='ring', half=False, out=None):
    ''' Convert Euler angles to coarser grid
    
    :Parameters:
    
    resolution : int
                 Pixel resolution
    theta : float or array
            Euler angle theta or array of Euler angles
    phi : float
          Euler angle phi or optional if theta is array of both
    scheme : str
             Pixel layout scheme: nest or ring
    half : bool
           Convert Euler angles to half volume
    out : array, optional
          Array of pixels for specified array of Euler angles
    
    :Returns:
    
    out : in or, array
          Pixel for specified Euler angles
    '''
    import healpix
    
    if scheme not in ('nest', 'ring'): raise ValueError, "scheme must be nest or ring"
    if hasattr(theta, '__iter__'):
        if phi is not None and not hasattr(phi, '__iter__'): 
            raise ValueError, "phi must be None or array when theta is an array"
        if hasattr(phi, '__iter__'): theta = zip(theta, phi)
        _ang2pix = getattr(healpix, 'ang2pix_%s'%scheme)
        _pix2ang = getattr(healpix, 'pix2ang_%s'%scheme)
        if out is None: out = numpy.zeros((len(theta), 2))
        i = 0
        for t, p in theta:
            t = _ensure_theta(t, half)
            pix = _ang2pix(int(resolution), float(t), float(p))
            out[i, :] = _pix2ang(int(resolution), int(pix))
            i += 1
        return out
    else:
        _ang2pix = getattr(healpix, 'ang2pix_%s'%scheme)
        if phi is None: "phi must not be None when theta is a float"
        theta = _ensure_theta(theta, half)
        return _ang2pix(int(resolution), float(theta), float(phi))


