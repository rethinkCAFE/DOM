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
"""
This module contains classes that serve as data containers for instrument geometry, extra
instrument information and scientific data and metadata. It also contains utility classes
used in conjunction with the data containers.
"""

from attribute import AttributeList
from information import Information, CompositeInformation
from instrument import Instrument
from comp_instrument import CompositeInstrument
from asg_instrument import ASG_Instrument
from indexselector import *
from nexus_id import NeXusId
from nxparameter import NxParameter
from roi import Roi
from sample import Sample
from simpleselector import *
from som import SOM
from so import PrimaryAxis
from so import SO

from DOM_version import version as __version__

# version
__id__ = "$Id$"
