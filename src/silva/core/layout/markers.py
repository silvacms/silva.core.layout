# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope import schema
from zope.app.interface import PersistentInterfaceClass
from zope.component import getUtility, getUtilitiesFor
from zope.component.interfaces import ObjectEvent
from zope.container.interfaces import IObjectAddedEvent
from zope.event import notify
from zope.interface import Interface
from zope.interface import providedBy, directlyProvides, directlyProvidedBy
from zope.interface.interfaces import IInterface
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
import zope.cachedescriptors.property

from persistent.list import PersistentList

from five import grok

# Zope 2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.interfaces import IObjectWillBeRemovedEvent

# Silva
from Products.Silva.helpers import add_and_edit

from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.layout.utils import findSite
from silva.core.services.base import ZMIObject
from silva.core.smi.interfaces import IPropertiesTab
from silva.core.smi.smi import SMIButton
from silva.translations import translate as _

from silva.core.layout.interfaces import ICustomizableType, ICustomizableTag, \
    ICustomizableMarker, IObjectHaveBeenMarked, IObjectHaveBeenUnmarked, \
    IObjectMarkEvent, IMarkManager

from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction

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
        ZMIObject.__init__(self)
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

    grok.implements(IObjectMarkEvent)

    def __init__(self, item, marker):
        super(ObjectMarkEvent, self).__init__(item)
        self.marker = marker


class ObjectHaveBeenMarked(ObjectMarkEvent):

    grok.implements(IObjectHaveBeenMarked)


class ObjectHaveBeenUnmarked(ObjectMarkEvent):

    grok.implements(IObjectHaveBeenUnmarked)


REGISTERED_TYPES = [IInterface, ICustomizableType,]

@grok.subscribe(CustomizationMarker, IObjectAddedEvent)
def registerMarker(marker, event):
    site = findSite(event.newParent)
    if site:
        sm = site.getSiteManager()
        marker.updateIdentifier()
        for iface_type in REGISTERED_TYPES:
            sm.registerUtility(marker, iface_type, marker.__identifier__)


@grok.subscribe(CustomizationMarker, IObjectWillBeRemovedEvent)
def unregisterMarker(marker, event):
    site = findSite(event.oldParent)
    for item in marker.markedObjects():
        IMarkManager(item).removeMarker(marker.__identifier__)
    if site:
        sm = site.getSiteManager()
        for iface_type in REGISTERED_TYPES:
            sm.unregisterUtility(marker, iface_type, marker.__identifier__)


@grok.subscribe(ISilvaObject, IObjectHaveBeenMarked)
def objectMarked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.addMarkedObject(item)


@grok.subscribe(ISilvaObject, IObjectHaveBeenUnmarked)
def objectUnmarked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.removeMarkedObject(item)


# Adapters

class MarkManager(grok.Adapter):

    grok.implements(IMarkManager)
    grok.context(ISilvaObject)
    grok.require('zope2.ManageProperties')

    def _listInterfaces(self, base):
        interfaces = providedBy(self.context).interfaces()
        return sorted([iface for iface in interfaces
                       if iface.extends(base)])

    def _fetchMarker(self, name):
        return getUtility(ICustomizableType, name=name)

    @zope.cachedescriptors.property.CachedProperty
    def usedInterfaces(self):
        return self._listInterfaces(ISilvaObject)

    @zope.cachedescriptors.property.CachedProperty
    def usedMarkers(self):
        return self._listInterfaces(ICustomizableTag)

    @zope.cachedescriptors.property.CachedProperty
    def availableMarkers(self):
        interfaces = getUtilitiesFor(ICustomizableType, context=self.context)
        availables = [interface for name, interface in interfaces
                      if interface.extends(ICustomizableTag)]
        return sorted(list(set(availables).difference(set(self.usedMarkers))))

    def removeMarker(self, marker):
        if isinstance(marker, basestring):
            marker = self._fetchMarker(marker)
        directlyProvides(
            self.context, directlyProvidedBy(self.context) - marker)
        notify(ObjectHaveBeenUnmarked(self.context, marker))

    def addMarker(self, marker):
        if isinstance(marker, basestring):
            marker = self._fetchMarker(marker)
        directlyProvides(
            self.context, directlyProvidedBy(self.context), marker)
        notify(ObjectHaveBeenMarked(self.context, marker))


# Forms to mark objects


def interfaceTerm(interface):
    """Create a vocabulary term to represent an interface.
    """
    title = interface.__doc__
    if '\n' in title:
        title = title.split('\n', 1)[0].strip()
    if not title:
        title = interface.__identifier__
    return SimpleTerm(token=interface.__identifier__,
                      value=interface,
                      title=title)


@grok.provider(IContextSourceBinder)
def usedInterfacesForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary(
        [interfaceTerm(interface)
         for interface in manager.usedInterfaces])


@grok.provider(IContextSourceBinder)
def usedMarkersForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary(
        [interfaceTerm(interface)
         for interface in manager.usedMarkers])


@grok.provider(IContextSourceBinder)
def availableMarkersForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary(
        [interfaceTerm(interface)
         for interface in manager.availableMarkers])


class IDisplayUsedInterfaces(Interface):

    usedInterface = schema.List(
        title=_(u"Used interfaces"),
        value_type=schema.Choice(
            source=usedInterfacesForContent),
        required=False)


class IRemoveCustomizationMarker(Interface):

    usedMarkers = schema.List(
        title=_(u"Used markers"),
        value_type=schema.Choice(
            source=usedMarkersForContent))


class IAddCustomizationMarker(Interface):

    availablesMarkers = schema.Set(
        title=_(u"Available markers"),
        value_type=schema.Choice(
            source=availableMarkersForContent))


class ContentInterfaces(grok.Adapter):
    grok.context(ISilvaObject)
    grok.provides(IDisplayUsedInterfaces)

    @property
    def usedInterface(self):
        manager = IMarkManager(self.context)
        return manager.usedInterfaces


class ManageCustomizeMarker(silvaforms.SMIComposedForm):
    """This form let you add and remove customization markers from the
    current content.
    """
    grok.context(ISilvaObject)
    grok.implements(IPropertiesTab)
    grok.name('tab_customization')
    grok.require('silva.ChangeSilvaContentSettings')

    tab = 'properties'

    label = _(u"customization markers")
    description = _(u"This screen let you tag your content with markers. "
                    u"Those markers can change how the content is displayed "
                    u"for instance.")


class DisplayUsedInterfaces(silvaforms.SMISubForm):
     grok.view(ManageCustomizeMarker)
     grok.order(10)
     grok.context(ISilvaObject)

     label = _(u"Used interfaces by the content which change its rendering")
     fields = silvaforms.Fields(IDisplayUsedInterfaces)
     mode = silvaforms.DISPLAY
     dataManager = silvaforms.makeAdaptiveDataManager(IDisplayUsedInterfaces)
     ignoreContent = False
     ignoreRequest = True


class AddCustomizationMarker(silvaforms.SMISubForm):
    grok.view(ManageCustomizeMarker)
    grok.order(20)
    grok.context(ISilvaObject)

    label = _(u"Add a marker to affect the content rendering")
    fields = silvaforms.Fields(IAddCustomizationMarker)

    def available(self):
        markerField = self.fields['availablesMarkers']
        return len(markerField.valueField.getChoices(self.context))

    @silvaforms.action(
        _(u"add"),
        description=_(u"mark the content with the selected marker(s)"))
    def add(self):
        values, errors = self.extractData()
        if not values.get('availablesMarkers', None):
            self.send_message(_(u"You need to select a marker."), type=u"error")
            return silvaforms.FAILURE

        manager = IMarkManager(self.context)
        for value in values['availablesMarkers']:
            manager.addMarker(value)
        self.status = _(u"Marker added.")
        return silvaforms.SUCCESS


class RemoveCustomizationMarker(silvaforms.SMISubForm):
    grok.view(ManageCustomizeMarker)
    grok.order(30)
    grok.context(ISilvaObject)

    label = _(u"Remove a marker")
    fields = silvaforms.Fields(IRemoveCustomizationMarker)

    def available(self):
        markerField = self.fields['usedMarkers']
        return len(markerField.valueField.getChoices(self.context))

    @silvaforms.action(
        _(u"remove"),
        description=_(u"remove the selected marker(s) from the content"),
        implements=IRemoverAction)
    def remove(self):
        values, errors = self.extractData()
        if not values.get('usedMarkers', None):
            self.send_message(_(u"You need to select a marker."), type=u"error")
            return silvaforms.FAILURE

        manager = IMarkManager(self.context)
        for value in values['usedMarkers']:
            manager.removeMarker(value)
        self.status = _(u"Marker removed.")
        return silvaforms.SUCCESS


class ManageCustomizationButton(SMIButton):
    grok.view(IPropertiesTab)
    grok.order(110)

    tab = 'tab_customization'
    label = _("customization")
