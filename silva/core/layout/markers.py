# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.app.interface import PersistentInterfaceClass
from zope.interface.interfaces import IInterface
from zope.component.interface import interfaceToName
from zope.app.container.interfaces import IObjectAddedEvent
from zope.interface import providedBy, directlyProvides, directlyProvidedBy
from zope.component import getUtility, getUtilitiesFor
import zope.cachedescriptors.property

# Zope 2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.interfaces import IObjectWillBeRemovedEvent

# Silva
from Products.Silva.BaseService import ZMIObject
from Products.Silva.helpers import add_and_edit
from Products.Silva.interfaces import ISilvaObject

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews

from interfaces import ISilvaCustomizableType, ISilvaCustomizableMarker
from customization import CustomizationManagementView, findSite

class CustomizationMarker(PersistentInterfaceClass, ZMIObject):

    meta_type = 'Silva Customization Marker'

    silvaconf.icon('markers.png')
    silvaconf.factory('manage_addCustomizationMarkerForm')
    silvaconf.factory('manage_addCustomizationMarker')

    def __init__(self, name, doc=None):
        self.id = name
        PersistentInterfaceClass.__init__(
            self, name=name, bases=(ISilvaCustomizableMarker,), __doc__=doc)
        ZMIObject.__init__(self, name)

    def updateIdentifier(self):
        self.__identifier__ = self.markerId()

    def markerId(self):
        return 'marker:%s' % '.'.join(self.getPhysicalPath()[1:])


manage_addCustomizationMarkerForm = PageTemplateFile(
    "www/customizationMarkerAdd", globals(),
    __name__='manage_addCustomizationMarkerForm')

def manage_addCustomizationMarker(self, name, REQUEST=None):
    """Add a Customization Marker.
    """

    marker = CustomizationMarker(name)
    self._setObject(name, marker)
    add_and_edit(self, name, REQUEST)
    return ''

REGISTERED_TYPES = [IInterface, ISilvaCustomizableType,]

@silvaconf.subscribe(CustomizationMarker, IObjectAddedEvent)
def registerMarker(marker, event):
    site = findSite(event.newParent)
    assert site
    sm = site.getSiteManager()
    marker.updateIdentifier()
    for iface_type in REGISTERED_TYPES:
        sm.registerUtility(marker, iface_type, marker.__identifier__)


@silvaconf.subscribe(CustomizationMarker, IObjectWillBeRemovedEvent)
def unregisterMarker(marker, event):
    site = findSite(event.oldParent)
    assert site
    sm = site.getSiteManager()
    for iface_type in REGISTERED_TYPES:
        sm.unregisterUtility(marker, iface_type, marker.__identifier__)



class ManageCustomizeMarker(silvaviews.ZMIView):

    silvaconf.name('manage_customization')
    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.context(ISilvaObject)


    def usedInterfaces(self, base=None):
        """Return used skinable interfaces for this item.
        """
        if base is None:
            base = ISilvaObject
        interfaces = providedBy(self.context).interfaces()
        return sorted([iface.__identifier__ for iface in interfaces if iface.extends(base)])

    @zope.cachedescriptors.property.CachedProperty
    def usedMarkers(self):
        """Return used markers interfaces for this item.
        """

        return self.usedInterfaces(ISilvaCustomizableMarker)

    @zope.cachedescriptors.property.CachedProperty
    def availablesMarkers(self):
        """Return availables markers.
        """

        interfaces = getUtilitiesFor(ISilvaCustomizableType, context=self.context)
        availables = [name for name, interface in interfaces if interface.extends(ISilvaCustomizableMarker)]
        return sorted(list(set(availables).difference(set(self.usedMarkers))))


class ManageEditCustomizeMarker(silvaviews.ZMIView):

    silvaconf.name('manage_editCustomization')
    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.context(ISilvaObject)

    def fetchMarker(self, name):
        return getUtility(ISilvaCustomizableType, name=name)

    def removeMarker(self, name):
        marker = self.fetchMarker(name)
        directlyProvides(self.context, directlyProvidedBy(self.context) - marker)

    def addMarker(self, name):
        marker = self.fetchMarker(name)
        directlyProvides(self.context, directlyProvidedBy(self.context), marker)
    
    def update(self):
        assert 'marker' in self.request.form
        if 'add' in self.request.form:
            for marker in self.request.form['marker']:
                self.addMarker(marker)
        elif 'remove' in self.request.form:
            for marker in self.request.form['marker']:
                self.removeMarker(marker)

        self.redirect(self.context.absolute_url() + '/manage_customization')

    def render(self):
        return 'Edit markers.'
