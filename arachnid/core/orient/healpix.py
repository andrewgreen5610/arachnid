''' pyHEALPix Library

It works with Euler angles in the ZYZ convention.

Resolution     nside       total    theta      half sphere (equator)  half sphere  half sphere sum
----------     -----       -----    -----      ---------------------  -----------  ---------------
1              2           48       29.32      28                     20           20
2              4           192      14.66      104                    88           108
3              8           768      7.33       400                    368          476
4              16          3072     3.66       1568                   1504         1980
5              32          12288    1.83       6208                   6080         8060
6              64          49152    0.92       24704                  24448        32508
7              128         196608   0.46       98560                  98048        130556
8              256         786432   0.23       393728                 392704       523260

.. Created on Aug 17, 2012
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
import logging, numpy, math


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

try:
    from core import _healpix
    _healpix;
    '''
    from _healpix import pix2ang_nest, \
                                  pix2ang_ring, \
                                  ang2pix_nest, ang2pix_ring, ring2nest, nest2ring, nside2npix, npix2nside
    pix2ang_nest, pix2ang_ring, ang2pix_nest, ang2pix_ring, ring2nest, nest2ring, nside2npix, npix2nside;
    '''
except:
    _logger.addHandler(logging.StreamHandler())
    _logger.exception("failed to import _healpix")
    #import core
    from ..app import tracing
    tracing.log_import_error("Failed to import pyHEALPix module - certain functionality will not be available", _logger)


def ensure_valid_deg(theta, phi, half=False):
    '''
    '''
    
    theta = pmod(theta, 180.0)
    phi = pmod(phi, 360.0)
    if half: return mirror_so2_deg(theta, phi)
    return theta,phi

def mirror_so2_deg(theta, phi):
    ''' Mirror the angles of a projection
    
    Assumes Euler ZYZ in degrees, psi,theta,phi
    
    :Parameters:
    
    theta : float
            Longitude 0 <= theta <= 180.0
    phi : float
            Latitude 0 <= theta <= 360.0
            
    :Returns:
    
    theta : float
            Longitude 0 <= theta <= 90.0
    phi : float
            Latitude 0 <= theta <= 360.0
    
    '''
    
    if theta > 180.0: 
        theta -= 180.0
    elif theta > 90.0:
        theta -= 90.0
        phi += 180.0
    theta = pmod(theta, 180.0)
    phi = pmod(phi, 360.0)
    return theta, phi

def mirror_so2(theta, phi):
    ''' Mirror the angles of a projection
    
    Assumes Euler ZYZ in radians, psi,theta,phi
    
    :Parameters:
    
    theta : float
            Longitude 0 <= theta <= 180.0
    phi : float
            Latitude 0 <= theta <= 360.0
            
    :Returns:
    
    theta : float
            Longitude 0 <= theta <= 90.0
    phi : float
            Latitude 0 <= theta <= 360.0
    
    '''
    
    if theta > numpy.pi: 
        theta -= numpy.pi
    elif theta > (numpy.pi/2):
        theta -= numpy.pi/2
        phi += numpy.pi
    return theta, phi

def angles(resolution, half=False, out=None):
    '''
    '''
    
    nsample = pow(2, resolution)
    npix = 12*nsample*nsample if not half else 6*nsample*nsample - nsample*2 # +nsample*2 add the equator projections
    ang = numpy.zeros(2)
    if out is None:
        out = numpy.zeros((npix, 3))
    for i in xrange(npix):
        _healpix.pix2ang_ring(nsample, i, ang)
        out[i, 1:]=numpy.rad2deg(ang)
    return out
    
def angles_gen(resolution, deg=False, half=False, out=None):
    '''
    '''
    
    nsample = pow(2, resolution)
    npix = 12*nsample*nsample if not half else 6*nsample*nsample - nsample*2
    ang = numpy.zeros(2)
    for i in xrange(npix):
        if deg:
            yield numpy.rad2deg(_healpix.pix2ang_ring(nsample, i, ang))
        else:
            yield _healpix.pix2ang_ring(nsample, i, ang)

def res2npix(resolution, half=False, equator=False):
    '''
    '''
    
    nsample = pow(2, resolution)
    if half:
        return 6*nsample*nsample + nsample*2 if equator else 6*nsample*nsample - nsample*2
    return 12*nsample*nsample

def theta2nside(theta, max_res=8):
    '''
    '''
    
    area = numpy.zeros(max_res)
    for i in xrange(1, area.shape[0]):
        area[i] = nside2pixarea(i)
    return numpy.argmin(numpy.abs(theta-area))+1

def pmod(x, y):
    ''' Result is always positive
    '''
    
    if y == 0: return x
    return x - y * math.floor(float(x)/y)
    
def nside2pixarea(resolution, degrees=False):
    """Give pixel area given nside.

    .. note::
        
        Raise a ValueError exception if nside is not valid.

    Examples:
    
    >>> import healpy as hpy
    >>> hpy.nside2pixarea(128, degrees = True)
    0.2098234113027917

    >>> hpy.nside2pixarea(256)
    1.5978966540475428e-05

    :Parameters:

    resolution : int
                 nside = 2**resolution
    degrees : bool
              if True, returns pixel area in square degrees, in square radians otherwise

    :Returns:

    pixarea : float
              pixel area in suqare radian or square degree
    """
    
    nsample = pow(2, resolution)
    npix = 12*nsample*nsample
    pixarea = 4*numpy.pi/npix
    if degrees: pixarea = numpy.rad2deg(numpy.rad2deg(pixarea))
    return numpy.sqrt(pixarea)

def pix2ang(resolution, pix, scheme='ring', half=False, out=None):
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
    
    resolution = pow(2, resolution)
    if scheme not in ('nest', 'ring'): raise ValueError, "scheme must be nest or ring"
    _pix2ang = getattr(_healpix, 'pix2ang_%s'%scheme)
    if hasattr(pix, '__iter__'):
        if out is None: out = numpy.zeros((len(pix), 2))
        for i in xrange(len(pix)):
            out[i, :] = _pix2ang(int(resolution), int(pix[i]))
        return out
    else:
        return _pix2ang(int(resolution), int(pix))

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
    
    resolution = pow(2, resolution)
    if scheme not in ('nest', 'ring'): raise ValueError, "scheme must be nest or ring"
    if hasattr(theta, '__iter__'):
        if phi is not None and not hasattr(phi, '__iter__'): 
            raise ValueError, "phi must be None or array when theta is an array"
        if hasattr(phi, '__iter__'): theta = zip(theta, phi)
        _ang2pix = getattr(_healpix, 'ang2pix_%s'%scheme)
        if out is None: out = numpy.zeros(len(theta), dtype=numpy.long)
        i = 0
        twopi=numpy.pi*2
        for t, p in theta:
            t = pmod(t, numpy.pi)
            p = pmod(p, twopi)
            if half: t, p = mirror_so2(t,p)
            out[i] = _ang2pix(int(resolution), float(t), float(p))
            i += 1
        return out
    else:
        _ang2pix = getattr(_healpix, 'ang2pix_%s'%scheme)
        if phi is None: "phi must not be None when theta is a float"
        theta = pmod(theta, numpy.pi)
        phi = pmod(phi, twopi)
        if half: theta, phi = mirror_so2(theta, phi)
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
    
    resolution = pow(2, resolution)
    if scheme not in ('nest', 'ring'): raise ValueError, "scheme must be nest or ring"
    if hasattr(theta, '__iter__'):
        if phi is not None and not hasattr(phi, '__iter__'): 
            raise ValueError, "phi must be None or array when theta is an array"
        if hasattr(phi, '__iter__'): theta = zip(theta, phi)
        _ang2pix = getattr(_healpix, 'ang2pix_%s'%scheme)
        _pix2ang = getattr(_healpix, 'pix2ang_%s'%scheme)
        if out is None: out = numpy.zeros((len(theta), 2))
        i = 0
        for t, p in theta:
            if half: t, p = mirror_so2(t,p)
            pix = _ang2pix(int(resolution), float(t), float(p))
            out[i, :] = _pix2ang(int(resolution), int(pix))
            i += 1
        return out
    else:
        _ang2pix = getattr(_healpix, 'ang2pix_%s'%scheme)
        if phi is None: "phi must not be None when theta is a float"
        if half: theta, phi = mirror_so2(theta, phi)
        return _ang2pix(int(resolution), float(theta), float(phi))


