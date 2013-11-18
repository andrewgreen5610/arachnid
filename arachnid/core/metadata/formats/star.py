''' Read/Write a table in the STAR format

This module reads from and writes to the STAR format, which is an
alternative to XML.

An example of the file:

.. container:: bottomnav, topic
    
    | data_images
    | loop\_
    | _rlnImageName
    | _rlnDefocusU
    | _rlnDefocusV
    | _rlnDefocusAngle
    | _rlnVoltage
    | _rlnAmplitudeContrast
    | _rlnSphericalAberration
    | 000001@/lmb/home/scheres/data/VP7/all_images.mrcs 13538 13985 109.45 300 0.15 2
    | 000002@/lmb/home/scheres/data/VP7/all_images.mrcs 13293 13796 109.45 300 0.15 2
    | 000003@/lmb/home/scheres/data/VP7/all_images.mcrs 13626 14085 109.45 300 0.15 2

It supports the following attributes:

    - Extension: star
    - Filter: Star (\*.star)

.. Created on Sep 28, 2010
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
from .. import format_utility
from ..factories import namedtuple_factory
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

def read_header(filename, header=[], factory=namedtuple_factory, **extra):
    '''Parses the header on the first line of the Star file
    
    .. sourcecode:: py
        
        >>> import os
        >>> os.system("more data.star")
        data_images
        loop_
        _rlnImageName
        _rlnDefocusU
        _rlnDefocusV
        _rlnDefocusAngle
        _rlnVoltage
        _rlnAmplitudeContrast
        _rlnSphericalAberration
        000001@/lmb/home/scheres/data/VP7/all_images.mrcs 13538 13985 109.45 300 0.15 2
        000002@/lmb/home/scheres/data/VP7/all_images.mrcs 13293 13796 109.45 300 0.15 2
        000003@/lmb/home/scheres/data/VP7/all_images.mcrs 13626 14085 109.45 300 0.15 2
        
        >>> header = []
        >>> fin = open("data.star", 'r')
        >>> factory, lastline = read_header(fin, header)
        >>> header
        ["_rlnImageName","_rlnDefocusU","_rlnDefocusV","_rlnDefocusAngle","_rlnVoltage","_rlnAmplitudeContrast","_rlnSphericalAberration"]
    
    :Parameters:
    
    filename : string or stream
               Input filename or stream
    header : list
             List of strings overriding parsed header
    factory : Factory
              Class or module that creates the container for the values returned by the parser
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    val : container
          Container with the given header values
    '''
    
    fin = open(filename, 'r') if isinstance(filename, str) else filename
    #lastline = ""
    try:
        while True: # Remove header comments
            line = fin.readline()
            if line == "": raise format_utility.ParseFormatError, "Not a star file or empty"
            if len(line) >= 5 and line[:5] == "data_": break
        while True:
            line = fin.readline()
            if line == "": raise format_utility.ParseFormatError, "Not a star file or empty"
            line = line.strip()
            if line != "": break
            
        tmpheader = []
        if line == "loop_":
            _logger.debug("Found loop - header has labels")
            while True:
                line = fin.readline()
                if line == "": raise format_utility.ParseFormatError, "Unexpected end of header"
                if line[0] != "_": break
                line = line.strip()
                idx = line.find('#')
                if idx != -1:
                    line = line[:idx].strip()
                tmpheader.append(line[1:])
            while line[0] == ';' or line[0] == '#' or line == "":
                line = fin.readline()
                if line == "": raise format_utility.ParseFormatError, "Unexpected end of file"
                line = line.strip()
            tot = len(line.strip().split())
        else:
            while line[0] == ';' or line[0] == '#':
                line = fin.readline()
                if line == "": raise format_utility.ParseFormatError, "Unexpected end of file"
                line = line.strip()
            tot = len(line.strip().split())
            tmpheader.extend(["column"+str(i+1) for i in xrange(tot)])
            logging.debug("create-header: "+str(header))
        
        if isinstance(header, dict):
            if len(header) == 0: raise ValueError, "Dictionary header cannot have zero elements"
            for key, val in header.iteritems():
                tmpheader[val] = key
        elif len(header) == 0: header.extend(tmpheader)
        if tot != len(header): raise format_utility.ParseFormatError, "Header does not match the file: %s"%header
        if isinstance(filename, str): fin.close()
        return factory.create(header, **extra), header, line
    except:
        fin.close()
        raise
    else:
        fin.close()
    raise format_utility.ParseFormatError, "Cannot parse header of Star document file - end of document"

def reader(filename, header=[], lastline="", numeric=False, columns=None, **extra):
    '''Creates a Star read iterator
    
    .. sourcecode:: py
        
        >>> import os
        >>> os.system("more data.star")
        data_images
        loop_
        _rlnImageName
        _rlnDefocusU
        _rlnDefocusV
        _rlnDefocusAngle
        _rlnVoltage
        _rlnAmplitudeContrast
        _rlnSphericalAberration
        000001@/lmb/home/scheres/data/VP7/all_images.mrcs 13538 13985 109.45 300 0.15 2
        000002@/lmb/home/scheres/data/VP7/all_images.mrcs 13293 13796 109.45 300 0.15 2
        
        >>> header = []
        >>> fin = open("data.star", 'r')
        >>> factory, lastline = read_header(fin, header)
        >>> header
        ["_rlnImageName","_rlnDefocusU","_rlnDefocusV","_rlnDefocusAngle","_rlnVoltage","_rlnAmplitudeContrast","_rlnSphericalAberration"]
        >>> map(factory, reader(fin, header, lastline, numeric=True))
        [ BasicTuple(rlnImageName="000001@/lmb/home/scheres/data/VP7/all_images.mrcs", rlnDefocusU=13538, rlnDefocusV=13985, rlnDefocusAngle=109.45, rlnVoltage=300, rlnAmplitudeContrast=0.15, rlnSphericalAberration=2), 
          BasicTuple(rlnImageName="000002@/lmb/home/scheres/data/VP7/all_images.mrcs", rlnDefocusU=13293, rlnDefocusV=13796, rlnDefocusAngle=109.45, rlnVoltage=300, rlnAmplitudeContrast=0.15, rlnSphericalAberration=2) ]
    
    :Parameters:
    
    filename : string or stream
               Input filename or input stream
    header : list
             List of strings overriding parsed header
    lastline : string
              Last line read by header parser, first line to parse
    numeric : boolean
              If true then convert string values to numeric
    columns : list
              List of columns to read otherwise None (all columns)
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    val : iterator
          Star read iterator
    '''
    
    fin = open(filename, 'r') if isinstance(filename, str) else filename
    try:
        if lastline != "":
            yield parse_line(lastline, numeric, columns, len(header))
        for line in fin:
            line = line.strip()
            if line == "" or line[0] == ';' or line[0] == '#': continue
            yield parse_line(line, numeric, columns, len(header))
    finally:
        fin.close()
        
def parse_line(line, numeric=False, columns=None, hlen=None):
    ''' Parse a line of values in the CSV format
    
        >>> parse_line("000001@/lmb/home/scheres/data/VP7/all_images.mrcs 13538 13985 109.45 300 0.15 2", True)
        ["000001@/lmb/home/scheres/data/VP7/all_images.mrcs", 13538, 13985, 109.45, 300, 0.15, 2]
    
    :Parameters:
    
    line : str
           String to parse
    numeric : boolean
              If true then convert string values to numeric
    columns : list
              List of columns to read otherwise None (all columns)
    hlen : int
           Number of elements in the header, optional
    
    :Returns:
    
    val : list
          List of values parsed from input line
    '''
    
    vals = line.split()
    if hlen is not None and hlen != len(vals): 
        raise format_utility.ParseFormatError, "Header length does not match values: "+str(hlen)+" != "+str(len(vals))+" --> "+str(vals)
    if columns is not None: vals = vals[columns]
    if numeric: return [format_utility.convert(v) for v in vals]
    return vals

############################################################################################################
# Write format                                                                                             #
############################################################################################################
def write(filename, values, factory=namedtuple_factory, **extra):
    '''Write a metadata (Star) file
    
    .. sourcecode:: py
        
        >>> BasicTuple = namedtuple("BasicTuple", "_rlnImageName,_rlnClassNumber,_rlnDefocusU")
        >>> values = [ BasicTuple("1/1", 1, 0.00025182), BasicTuple("1/2", 1, 0.00023578) ]
        >>> write("data.star", values)
        
        >>> import os
        >>> os.system("more data.star")
        id,select,peak
        1/1,1,0.00025182
        1/2,1,0.00023578
    
    :Parameters:
    
    filename : string or stream
               Output filename or stream
    values : container
             Value container such as a list or an ndarray
    factory : Factory
              Class or module that creates the container for the values returned by the parser
    extra : dict
            Unused keyword arguments
    '''
    
    fout = open(filename, 'w') if isinstance(filename, str) else filename
    write_header(fout, values, factory, **extra)
    write_values(fout, values, factory, **extra)
    if isinstance(filename, str): fout.close()
    
def write_header(filename, values, factory=namedtuple_factory, tag="", blockcode="images", **extra):
    '''Write a comma separated value (Star) header
    
    .. sourcecode:: py
        
        >>> BasicTuple = namedtuple("BasicTuple", "id,select,peak")
        >>> values = [ BasicTuple("1/1", 1, 0.00025182), BasicTuple("1/2", 1, 0.00023578) ]
        >>> write_header("data.star", values)
        
        >>> import os
        >>> os.system("more data.star")
        data_images
        loop_
        _rlnImageName
        _rlnDefocusU
        _rlnDefocusV
        _rlnDefocusAngle
        _rlnVoltage
        _rlnAmplitudeContrast
        _rlnSphericalAberration
    
    :Parameters:
    
    filename : string or stream
               Output filename or stream
    values : container
             Value container such as a list or an ndarray
    factory : Factory
              Class or module that creates the container for the values returned by the parser
    tag : str
          Tag for each header value, e.g. tag=rln
    blockcode : str
                Label for the data block
    extra : dict
            Unused keyword arguments
    '''
    
    fout = open(filename, 'w') if isinstance(filename, str) else filename
    fout.write('data_'+blockcode+'\n')
    fout.write('loop_\n')
    header = factory.get_header(values, **extra)
    for h in header:
        fout.write("_"+tag+h+'\n')
    if isinstance(filename, str): fout.close()
    
def write_values(filename, values, factory=namedtuple_factory, header=None, star_separtor=' ', **extra):
    '''Write comma separated value (Star) values
    
    .. sourcecode:: py
        
        >>> BasicTuple = namedtuple("BasicTuple", "id,select,peak")
        >>> values = [ BasicTuple("1/1", 1, 0.00025182), BasicTuple("1/2", 1, 0.00023578) ]
        >>> write_values("data.star", values)
        
        >>> import os
        >>> os.system("more data.star")
        1/1,1,0.00025182
        1/2,1,0.00023578
    
    :Parameters:
    
    filename : string or stream
               Output filename or stream
    values : container
             Value container such as a list or an ndarray
    factory : Factory
              Class or module that creates the container for the values returned by the parser
    extra : dict
            Unused keyword arguments
    '''
    
    fout = open(filename, 'w') if isinstance(filename, str) else filename
    header = factory.get_header(values, offset=True, header=header, **extra)
    for v in values:
        vals = factory.get_values(v, header, float_format="%11g", **extra)
        fout.write(star_separtor.join(vals)+"\n")
    if isinstance(filename, str): fout.close()
        
############################################################################################################
# Extension and Filters                                                                                    #
############################################################################################################

def extension():
    '''Get extension of Star format
    
    :Returns:
    
    val : string
          File extension - star
    '''
    
    return "star"

def filter():
    '''Get filter of Star format
    
    :Returns:
    
    val : string
          File filter - Star (\*.star)
    '''
    
    return "Star (*.star)"



