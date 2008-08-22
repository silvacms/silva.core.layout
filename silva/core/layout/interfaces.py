# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface.interfaces import IInterface
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


# Interfaces types

class ICustomizableType(IInterface):
    """This type represent customizable interface in Silva. THIS IS
    NOT AN INTERFACE TO PROVIDES OR IMPLEMENTS.
    """

class ILayerType(IInterface):
    """This type represent Silva layer. THIS NOT AND INTERFACE TO
    PROVIDES OR IMPLEMENTS.
    """

# Interfaces

class ICustomizable(Interface):
    """Marker customizable objects.
    """

class ICustomizableTag(ICustomizable):
    """This is a tag that you can set on object to customize them.
    """

class ICustomizableMarker(ICustomizableTag):
    """Customizable markers.
    """

# Adapters

class IMarkManager(Interface):
    """A Mark manager. This let you manage marks on object, so they
    can be customized after using them.
    """

    usedInterfaces = Attribute(u"Skinable interfaces used")
    usedMarkers = Attribute(u"Skinable markers set on the object")
    availablesMarkers = Attribute(u"Skinable markers that can be set  on the object")
    
    def addMarker(name):
        """Set marker name in the object.
        """

    def removeMarker(name):
        """Remove marker name from the object.
        """

# Utility

class ICustomizationService(Interface):
    """A customization manager let you customize templates.
    """

    def availablesInterfaces(base=ICustomizable):
        """List availables interfaces, which can be used to search
        view to customize.
        """

    def availablesLayers(base=IDefaultBrowserLayer):
        """List availables layers, for which you can customize views.
        """

    def availablesTemplates(interface, layer=IDefaultBrowserLayer):
        """List availables templates for that interface and layer.
        """

# Events

class IObjectMarkEvent(Interface):
    """A marker have been involved with an object.
    """

    marker = Attribute(u"Involved marker")

class IObjectHaveBeenMarked(IObjectMarkEvent):
    """An object have been marked by a marker.
    """

class IObjectHaveBeenUnmarked(IObjectMarkEvent):
    """A Marker have been removed from an object.
    """
