#                        Data Object Model
#           A part of the SNS Analysis Software Suite.
#
#                  Spallation Neutron Source
#          Oak Ridge National Laboratory, Oak Ridge TN.
#
#
#                             NOTICE
#
# For this software and its associated documentation, permission is granted
# to reproduce, prepare derivative works, and distribute copies to the public
# for any purpose and without fee.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government.  Neither the United States Government nor the
# United States Department of Energy, nor any of their employees, makes any
# warranty, express or implied, or assumes any legal liability or
# responsibility for the accuracy, completeness, or usefulness of any
# information, apparatus, product, or process disclosed, or represents that
# its use would not infringe privately owned rights.
#

# $Id$

import dst_base
import dst_utils
import math
import SOM

class Ascii3ColDST(dst_base.DST_BASE):
    """
    This class creates a N column ASCII file with a metadata header. The
    formatting is based on the
    U{spec<http://www.certif.com/spec_manual/user_1_4_1.html>} file format.
    
    @cvar MIME_TYPE: The MIME-TYPE of the class
    @type MIME_TYPE: C{string}
    
    @cvar EMPTY: Variable for holding an empty string
    @type EMPTY: C{string}
    
    @cvar SPACE: Variable for holding a space
    @type SPACE: C{string}

    @ivar __file: The handle to the output data file
    @type __file: C{file}

    @ivar __epoch: The epoch (UNIX time) when the object was instantiated.
                   This is used as the creation time of the file information.
    @type __epoch: C{string} 

    @ivar __columns: The number of independent, dependent axes and associated
                     uncertainies in the data.
    @type __columns: C{int}

    @ivar __data_type: The dataset type for the incoming data. The available
                       types are I{histogram}, I{coordinate} and I{density}.
    @type __data_type: C{string}

    @ivar __axis_and_units: The string containing the axis labels and units
                            for both independent and dependent axes derived
                            from the incoming dataset information.
    @type __axis_and_units: C{string}

    @ivar __counter: A running index of the number of spectra being written
                     to file.
    @type __counter: C{int}
    """
    
    MIME_TYPE = "text/Spec"
    EMPTY = ""
    SPACE = " "
    
    ########## DST_BASE functions

    def __init__(self, resource, *args, **kwargs):
        """
        Object constructor

        @param resource: The handle to the output data file
        @type resource: C{file}

        @param args: Argument objects that the class accepts (UNUSED)

        @param kwargs: A list of keyword arguments that the class accepts:
        """
        import time
        
        self.__file = resource
        self.__epoch = time.time()
        self.__columns = 0

    def release_resource(self):
        """
        This method closes the file handle to the output file.
        """
        self.__file.close()

    def getSOM(self, som_id=None):
        """
        This method parses the resource and creates a SOM from the information.

        @param som_id: The name of the SOM. The default value is C{None}. This
        retrieves all information. 
        """
        som = SOM.SOM()

        som.attr_list = dst_utils.parse_spec_header(self.__file)

        return som

    def writeSO(self, so):
        """
        This method writes the L{SOM.SO} information to the output file.

        @param so: The object to have its information written to file.
        @type so: L{SOM.SO}
        """
        self.writeData(so)

    def writeSOM(self, som, **kwargs):
        """
        This method writes the L{SOM.SOM} information to the output file.

        @param som: The object to have its information written to file.
        @type som: L{SOM.SOM}

        @param kwargs: A list of keyword arguments that the method accepts:

        @keyword extra_som: Parameter to provide another L{SOM.SOM} containing
                            information that should be written to the file.
        @type extra_som: L{SOM.SOM}


        @exception RuntimeError: Is raised if the current C{SOM.SOM} and the
                                 extra C{SOM.SOM} have incompatible data types.
        """
        self.__data_type = som.getDataSetType()
        try:
            extra_som = kwargs["extra_som"]
        except KeyError:
            extra_som = None

        if extra_som is not None and \
               self.__data_type != extra_som.getDataSetType():
            raise RuntimeError("The SOMs are not the same data type: "\
                           +"%s, extra_som=%s" % (self._data_type,
                                                  extra_som.getDataSetType()))
        
        dst_utils.write_spec_header(self.__file, self.__epoch, som)
        (format_str, names) = self.__formatDataInfo(som, extra_som)
        self.__axes_and_units =  format_str % names
        self.__counter = 1
        if extra_som is None:
            for so in som:
                self.writeData(so)
        else:
            import itertools
            for so_tuple in itertools.izip(som, extra_som):
                self.writeData(so_tuple[0], so_tuple[1])

    ########## Special functions

    def __dataSelfCheck(self, som):
        """
        This private method cross-checks the two locations in a L{SOM.SOM}
        that store the dimension information.

        @param som: The object to have its dimensions cross-checked
        @type som: L{SOM.SOM}


        @exception RuntimeError: Is raised is the two dimensions do not match
        """
        # Need SO for primary axis information
        so = som[0]
        dim = som.getDimension()

        if dim != so.dim():
            raise RuntimeError("SOM and attending SOs do not have the same"\
                               +" dimensions")

    def __formatDataInfo(self, som, som1=None):
        """
        This private method creates a full format string and the associated
        axis labels and units for the independent and dependent axes and
        associated uncertainties contained within the incoming dataset.

        @param som: The object containing the information about all axes.
        @type som: L{SOM.SOM}

        @param som1: Optional object containing the information about all axes.
        @type som1: L{SOM.SOM}
        

        @return: A format string and the axis labels and units.
        @rtype: C{tuple} (C{string}, (C{list} of C{string}s))
        """
        self.__dataSelfCheck(som)

        names = []
        result = ["#L"];

        if som1 is not None:
            self.__dataSelfCheck(som1)
            (names, result) = self.__setPrimaryAxisInfo(som1.getDimension(),
                                                        som1, som1[0],
                                                        names, result)

        (names, result) = self.__setPrimaryAxisInfo(som.getDimension(), som,
                                                    som[0], names, result)

        # Add y and var_y axis format positions
        result.append("%s(%s)  Sigma(%s)")
        names.append(som.getYLabel())
        names.append(som.getYUnits())
        names.append(som.getYUnits())
        self.__columns += 2

        return (self.SPACE.join(result), tuple(names))

    def __setPrimaryAxisInfo(self, dim, som, so, names, result):
        """
        This private method sets the formatting strings for the L{SOM.SOM}s
        independent axes.

        @param dim: The dimension of the incoming dataset
        @type dim: C{int}

        @param som: The object containing the information about the independent
                    axes.
        @type som: L{SOM.SOM}

        @param so: The object containing information about associated
                   uncertainties for the independent axes.
        @type so: L{SOM.SO}

        @param names: The placeholder for the axis labels and units
        @type names: C{list}
        
        @param result: The placeholder for the 
        @type result: C{list} of C{string}s


        @return: A pair of C{string} C{list}s containing the axis labels and
                 units and the associated format strings.
        @rtype: C{tuple} of two C{list}s of C{string}s
        """
        # Add primary axis format positions
        for i in range(dim):
            self.__columns += 1
            result.append("%s(%s) ")
            names.append(som.getAxisLabel(i))
            names.append(som.getAxisUnits(i))
            if so.axis[i].var is not None:
                self.__columns += 1
                result.append("Sigma(%s) ")
                names.append(som.getAxisUnits(i))

        return (names, result)

    def writeData(self, so, so1=None):
        """
        This method is responsible for writing the actual data contained within
        the L{SOM.SO}s to the attached file. 

        @param so: Object containing data to be written to file
        @type so: L{SOM.SO}

        @param so1: Optional object containing data to be written to file
        @type so1: L{SOM.SO}
        """
        print >> self.__file, self.EMPTY
        print >> self.__file, "#S", self.__counter, "Spectrum ID", so.id
        print >> self.__file, "#N", self.__columns
        print >> self.__file, self.__axes_and_units
        so_y_len = len(so.y)

        size = so_y_len
        if self.__data_type == "" or self.__data_type == "histogram":
            size += 1
        # Density data does not need to be incremented by one
        else:
            pass
        
        for i in range(size):
            if so1 is not None:
                dim1 = so1.dim()
                for k in range(dim1):
                    print >> self.__file, so1.axis[k].val[i], self.SPACE,
                    if so1.axis[k].var is not None:
                        try:
                            print >> self.__file, \
                                  math.sqrt(math.fabs(so1.axis[k].var[i])),
                        except OverflowError:
                            print >> self.__file, float('inf'),
            
            dim = so.dim()
            for j in range(dim):
                print >> self.__file, so.axis[j].val[i], self.SPACE,
                if so.axis[j].var is not None:
                    try:
                        print >> self.__file, \
                              math.sqrt(math.fabs(so.axis[j].var[i])), \
                              self.SPACE,
                    except OverflowError:
                        print >> self.__file, float('inf'), self.SPACE,     

            if i < so_y_len:
                print >> self.__file, so.y[i],self.SPACE,
                try:
                    print >> self.__file, math.sqrt(math.fabs(so.var_y[i]))
                except OverflowError:
                    print >> self.__file, float('inf')
            else:
                print >> self.__file, self.EMPTY

        self.__counter += 1
