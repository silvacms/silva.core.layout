# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface.interfaces import IInterface
from zope.interface import Interface

# Interfaces types

class ISilvaCustomizableType(IInterface):
    """This type represent customizable interface in Silva. THIS IS
    NOT AN INTERFACE TO PROVIDES OR IMPLEMENTS.
    """

class ISilvaLayerType(IInterface):
    """This type represent Silva layer. THIS NOT AND INTERFACE TO
    PROVIDES OR IMPLEMENTS.
    """

# Interfaces

class ISilvaCustomizable(Interface):
    """Marker customizable objects.
    """

class ISilvaCustomizableMarker(ISilvaCustomizable):
    """Customizable markers.
    """
