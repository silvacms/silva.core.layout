# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


# Interfaces

class ICustomizableTag(Interface):
    """This is a tag that you can set on object to customize them.
    """


# Default skin and layers

class ICustomizableLayer(IDefaultBrowserLayer):
    """A customizable layer.
    """


class ISMILayer(ICustomizableLayer):
    """SMI objects.
    """


class ISilvaLayer(ICustomizableLayer):
    """Default Silva Layer
    """


class ISilvaSkin(ISilvaLayer, IBrowserSkinType):
    """A Silva skin for the default layer.
    """

