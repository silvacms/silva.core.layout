# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.interface import PersistentInterfaceClass
from zope.app.intid.interfaces import IIntIds
from zope.component.interfaces import ObjectEvent
from zope.component import getUtility, getUtilitiesFor
from zope.interface.interfaces import IInterface
from zope.interface import providedBy, directlyProvides, directlyProvidedBy
from zope.event import notify
import zope.cachedescriptors.property

from persistent.list import PersistentList

from grokcore import component

# Zope 2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.interfaces import IObjectWillBeRemovedEvent

# Silva
from Products.Silva.BaseService import ZMIObject
from Products.Silva.helpers import add_and_edit

from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.views import views as silvaviews

from interfaces import ICustomizableType, ICustomizableTag, ICustomizableMarker
from interfaces import IObjectHaveBeenMarked, IObjectHaveBeenUnmarked
from interfaces import IObjectMarkEvent, IMarkManager
from utils import findSite


# Marker object

class CustomizationMarker(PersistentInterfaceClass, ZMIObject):

    meta_type = 'Silva Customization Marker'

    silvaconf.icon('markers.png')
    silvaconf.factory('manage_addCustomizationMarkerForm')
    silvaconf.factory('manage_addCustomizationMarker')

    def __init__(self, name, doc=None):
        self.id = name
        PersistentInterfaceClass.__init__(
            self, name=name, bases=(ICustomizableMarker,), __doc__=doc)
        ZMIObject.__init__(self, name)
        self.marked = PersistentList()

    def updateIdentifier(self):
        self.__identifier__ = self.markerId()

    def addMarkedObject(self, obj):
        oid = getUtility(IIntIds).register(obj)
        self.marked.append(oid)

    def removeMarkedObject(self, obj):
        oid = getUtility(IIntIds).getId(obj)
        self.marked.remove(oid)

    def markedObjects(self):
        resolver = getUtility(IIntIds).getObject
        return [resolver(oid) for oid in self.marked]

    def markerId(self):
        return u'marker:%s' % '.'.join(self.getPhysicalPath()[1:])


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



# Event arround markers

class ObjectMarkEvent(ObjectEvent):

    component.implements(IObjectMarkEvent)

    def __init__(self, item, marker):
        super(ObjectMarkEvent, self).__init__(item)
        self.marker = marker


class ObjectHaveBeenMarked(ObjectMarkEvent):

    component.implements(IObjectHaveBeenMarked)


class ObjectHaveBeenUnmarked(ObjectMarkEvent):

    component.implements(IObjectHaveBeenUnmarked)


REGISTERED_TYPES = [IInterface, ICustomizableType,]

@silvaconf.subscribe(CustomizationMarker, IObjectAddedEvent)
def registerMarker(marker, event):
    site = findSite(event.newParent)
    if site:
        sm = site.getSiteManager()
        marker.updateIdentifier()
        for iface_type in REGISTERED_TYPES:
            sm.registerUtility(marker, iface_type, marker.__identifier__)


@silvaconf.subscribe(CustomizationMarker, IObjectWillBeRemovedEvent)
def unregisterMarker(marker, event):
    site = findSite(event.oldParent)
    for item in marker.markedObjects():
        IMarkManager(item).removeMarker(marker.__identifier__)
    if site:
        sm = site.getSiteManager()
        for iface_type in REGISTERED_TYPES:
            sm.unregisterUtility(marker, iface_type, marker.__identifier__)


@silvaconf.subscribe(ISilvaObject, IObjectHaveBeenMarked)
def objectMarked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.addMarkedObject(item)


@silvaconf.subscribe(ISilvaObject, IObjectHaveBeenUnmarked)
def objectUnmarked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.removeMarkedObject(item)


# Adapters

class MarkManager(component.Adapter):

    component.implements(IMarkManager)
    silvaconf.context(ISilvaObject)
    silvaconf.require('zope2.ManageProperties')

    def _listInterfaces(self, base):
        interfaces = providedBy(self.context).interfaces()
        return sorted([iface.__identifier__ for iface in interfaces if iface.extends(base)])

    def _fetchMarker(self, name):
        return getUtility(ICustomizableType, name=name)

    @zope.cachedescriptors.property.CachedProperty
    def usedInterfaces(self):
        return self._listInterfaces(ISilvaObject)

    @zope.cachedescriptors.property.CachedProperty
    def usedMarkers(self):
        return self._listInterfaces(ICustomizableTag)

    @zope.cachedescriptors.property.CachedProperty
    def availablesMarkers(self):
        interfaces = getUtilitiesFor(ICustomizableType, context=self.context)
        availables = [name for name, interface in interfaces if interface.extends(ICustomizableTag)]
        return sorted(list(set(availables).difference(set(self.usedMarkers))))

    def removeMarker(self, name):
        marker = self._fetchMarker(name)
        directlyProvides(self.context, directlyProvidedBy(self.context) - marker)
        notify(ObjectHaveBeenUnmarked(self.context, marker))

    def addMarker(self, name):
        marker = self._fetchMarker(name)
        directlyProvides(self.context, directlyProvidedBy(self.context), marker)
        notify(ObjectHaveBeenMarked(self.context, marker))


# Forms to mark objects

class ManageCustomizeMarker(silvaviews.ZMIView):

    silvaconf.name('manage_customization')
    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.context(ISilvaObject)

    def update(self):
        manager = IMarkManager(self.context)
        self.usedInterfaces = manager.usedInterfaces
        self.usedMarkers = manager.usedMarkers
        self.availablesMarkers = manager.availablesMarkers


class ManageEditCustomizeMarker(silvaviews.ZMIView):

    silvaconf.name('manage_editCustomization')
    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.context(ISilvaObject)

    def update(self):
        assert 'marker' in self.request.form
        manager = IMarkManager(self.context)
        if 'add' in self.request.form:
            for marker in self.request.form['marker']:
                manager.addMarker(marker)
        elif 'remove' in self.request.form:
            for marker in self.request.form['marker']:
                manager.removeMarker(marker)

        self.redirect(self.context.absolute_url() + '/manage_customization')

    def render(self):
        return 'Edit markers.'


