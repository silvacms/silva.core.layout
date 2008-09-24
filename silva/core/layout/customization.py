# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.app.component.interfaces import ISite
from zope.configuration.name import resolve
from zope.component import getGlobalSiteManager, queryAdapter
from zope.component import getUtility, getUtilitiesFor
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import zope.cachedescriptors.property

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
from OFS.interfaces import IObjectWillBeRemovedEvent
from zExceptions import BadRequest

from Products.Silva.BaseService import SilvaService
from Products.Silva.helpers import add_and_edit
from Products.Silva.interfaces import ISilvaObject

from silva.core import conf as silvaconf
from silva.core.views.ttwtemplates import TTWViewTemplate
from silva.core.views.interfaces import ITemplate, ICustomizedTemplate
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.views.interfaces import ITemplateNotCustomizable
from silva.core.views import views as silvaviews

import interfaces
from interfaces import ICustomizable, ICustomizableType
from interfaces import ICustomizableMarker, ILayerType

from utils import findSite, findNextSite, queryAdapterOnClass

from five import grok

class ViewManager(grok.Adapter):

    grok.implements(interfaces.IViewManager)
    grok.adapts(ISilvaObject)


    def sites(self):
        """Gives a list of local sites.
        """
        site = findNextSite(self.context)
        while not (site is None):
            yield (site.getSiteManager(), u'/'.join(site.getPhysicalPath()))
            site = findNextSite(site)
        yield (getGlobalSiteManager(), None)


    def _entry(self, reg, sitename):
        """Build a ViewEntry from the registration info.
        """
        if ITemplateNotCustomizable.implementedBy(reg.factory):
            return None
        entry = queryAdapterOnClass(reg.factory, interfaces.IViewEntry)
        if entry is None:
            entry = queryAdapter(reg.factory, interfaces.IViewEntry)
            if entry is None:
                if isAFiveTemplate(reg.factory):
                    entry = FiveViewEntry(reg.factory)
                    
        if not (entry is None):
            entry.origin = sitename
            entry.registration = reg

        return entry            


    def search(self, interface, layer, sort=False):
        """Search and return all ViewEntry object for customizable
        views for interface in layer layer.
        """

        def viewsFor(site, sitename):
            for reg in site.registeredAdapters():
                if (len(reg.required) >= 2 and
                    interface.isOrExtends(reg.required[0]) and
                    reg.required[0].isOrExtends(ICustomizable) and
                    reg.required[1].isOrExtends(layer)):
                    
                    entry = self._entry(reg, sitename)
                    if entry:
                        yield entry

        views = []
        for site in self.sites():
            views.extend(viewsFor(*site))

        if sort is True:
            return sorted(views, key=lambda e: e.name)
        return views


    def get(self, type_, name, origin, required):
        """Retrieve the ViewEntry which correspond to the given settings.
        """
        for site, sitename in self.sites():
            if sitename != origin:
                continue
            for reg in site.registeredAdapters():
                if (reg.required == required and
                    reg.name == name and
                    reg.provided == type_):
                    return self._entry(reg, sitename)
            return None
        return None


class DefaultViewEntry(grok.Adapter):
    """Default base class for view entries.
    """

    grok.implements(interfaces.IViewEntry)
    grok.baseclass()

    type_ = u'Five Page Template'
    template = None
    config = None
    origin = None

    registration = None
    
    @property
    def name(self):
        return self.registration.name

    @property
    def for_(self):
        return self.registration.required[0].__identifier__

    @property
    def layer(self):
        return self.registration.required[1].__identifier__

    @property
    def signature(self):
        required = ':'.join(map(lambda x: x.__identifier__, self.registration.required))
        return '%s:%s:%s:%s' % (self.registration.provided.__identifier__,
                                self.registration.name,
                                self.origin,
                                required)

    @property
    def code(self):
        if self.template:
            return open(self.template, 'rb').read()
        return u''

    def generateId(self):
        tid = '-'.join(map(lambda r: r.__identifier__.split('.')[-1],
                           self.registration.required))
        return '%s-%s' % (tid, self.name)

    def permission(self):
        permissions = self.context.__ac_permissions__
        for permission, methods in permissions:
            if methods[0] in ('', '__call__',):
                return permission
        return None

    def customize(self, where, customized_for=None, customized_layer=None):

        if customized_for is None:
            customized_for = self.registration.required[0]
        if customized_layer is None:
            customized_layer = self.registration.required[1]

        template_id = str(self.generateId())
        viewclass = self.context.__bases__[0]
        permission = self.permission()
        service = getUtility(interfaces.ICustomizationService)
        new_template = TTWViewTemplate(template_id, self.code, 
                                       view=viewclass, permission=permission)
        
        service._setObject(template_id, new_template)
        new_template = getattr(service, template_id)

        required = list(self.registration.required)
        required[0] = customized_for
        required[1] = customized_layer
        
        manager = findSite(service).getSiteManager()
        manager.registerAdapter(new_template, 
                                required=tuple(required),
                                provided=self.registration.provided, 
                                name=self.registration.name)

        return new_template


class GrokViewEntry(DefaultViewEntry):
    """A Grok View.
    """

    grok.context(ITemplate)

    type_ = u'Grok Page Template'

    @property
    def template(self):
        if hasattr(self.context, 'template'):
            return self.context.template._template.filename
        return None

    def generateId(self):
        return 'grok-template-%s' % super(GrokViewEntry, self).generateId()

class GrokContentProviderEntry(GrokViewEntry):
    """A Grok Content Provider.
    """

    grok.context(IContentProvider)

    type_ = u'Grok Content Provider'

    def generateId(self):
        return 'grok-contentprovider-%s' % super(GrokViewEntry, self).generateId()


class GrokViewletEntry(GrokViewEntry):
    """A Grok Viewlet.
    """

    grok.context(IViewlet)

    type_ = u'Grok Viewlet'

    def generateId(self):
        return 'grok-viewlet-%s' % super(GrokViewEntry, self).generateId()


class CustomizedViewEntry(DefaultViewEntry):
    """A Customized View.
    """

    grok.context(ICustomizedTemplate)

    type_ = u'Customized Page Template'

    @property
    def template(self):
        return self.context.id

    @property
    def code(self):
        return self.context.read()

    def generateId(self):
        return 'customized-%s' % super(CustomizedViewEntry, self).generateId()


class FiveViewEntry(DefaultViewEntry):
    """A regular Five template.
    """

    grok.baseclass()

    @property
    def config(self):
        return self.registration.info.file

    @property
    def template(self):
        return self.context.index.filename

    def generateId(self):
        return 'five-template-%s' % super(FiveViewEntry, self).generateId()



def isAFiveTemplate(factory):
    """There is no interfaces for Five templates. That's the hack to
    guess it's an five template.
    """
    return (hasattr(factory, '__name__') and factory.__name__.startswith('SimpleViewClass'))


class CustomizationService(Folder, SilvaService):

    meta_type = 'Silva Customization Service'

    silvaconf.icon('customization.png')
    silvaconf.factory('manage_addCustomizationServiceForm')
    silvaconf.factory('manage_addCustomizationService')

    grok.implements(interfaces.ICustomizationService)

    manage_options = (
        {'label':'Customize', 'action':'manage_customization'},
        ) + Folder.manage_options


    def availablesInterfaces(self, base=ICustomizable):
        interfaces = getUtilitiesFor(ICustomizableType, context=self)
        return sorted([name for name, interface in interfaces if interface.isOrExtends(base)])

    def availablesLayers(self, base=IDefaultBrowserLayer):
        layers = getUtilitiesFor(ILayerType)
        return sorted([name for name, layer in layers if layer.isOrExtends(base)])

    def availablesTemplates(self, interface, layer=IDefaultBrowserLayer):
        return interfaces.IViewManager(self).search(interface, layer, sort=True)


class CustomizationManagementView(silvaviews.ZMIView):

    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.baseclass()

    interface = None
    layer = None

    def availablesInterfaces(self):
        """Return available interfaces starting from base.
        """
        base = self.interface
        if base is None:
            base = ICustomizable

        return self.context.availablesInterfaces(base)

    def availablesInterfacesAndMarkers(self):
        """Return available interfaces starting from base and markers.
        """
        interfaces = self.availablesInterfaces()
        interfaces.extend(self.context.availablesInterfaces(ICustomizableMarker))
        return interfaces

    def availablesLayers(self):
        """Return available layers starting from base.
        """
        base = self.layer
        if base is None:
            base = IDefaultBrowserLayer

        return self.context.availablesLayers(base)


class ManageCustomTemplates(CustomizationManagementView):

    silvaconf.name('manage_customization')

    def update(self):
        self.availableTemplates = []
        self.selectedInterface = self.request.form.get('interface', None)
        self.selectedLayer = self.request.form.get('layer', IDefaultBrowserLayer.__identifier__)

        if self.selectedInterface:
            interface = getUtility(ICustomizableType, name=self.selectedInterface)
            layer = getUtility(ILayerType, name=self.selectedLayer)

            self.availableTemplates = self.context.availablesTemplates(interface, layer)
        else:
            self.selectedInterface = ISilvaObject.__identifier__
        

class ManageViewTemplate(CustomizationManagementView):

    silvaconf.name('manage_template')

    def update(self):
        assert 'signature' in self.request.form

        signature = self.request.form['signature'].split(':')
        type_ = resolve(signature[0])
        name = signature[1]
        origin = signature[2] != 'None' and signature[2] or None
        required = tuple(map(resolve, signature[3:]))
        assert len(required) > 1
        self.interface = required[0]
        self.layer = required[1]

        self.entry = interfaces.IViewManager(self.context).get(type_, name, origin, required)
        if self.entry is None:
            raise ValueError, 'Template not found'


class ManageCreateCustomTemplate(ManageViewTemplate):

    silvaconf.name('manage_createCustom')

    def update(self):
        super(ManageCreateCustomTemplate, self).update()

        for_name = self.request.form['customize_for']
        layer_name = self.request.form['customize_layer']
        customize_for = getUtility(ICustomizableType, name=for_name)
        customize_layer = getUtility(ILayerType, name=layer_name)

        new_template = self.entry.customize(self, customize_for, customize_layer)

        self.redirect(new_template.absolute_url() + '/manage_workspace')

                                       
    def render(self):
        return u'Customized.'


manage_addCustomizationServiceForm = PageTemplateFile(
    "www/customizationServiceAdd", globals(),
    __name__='manage_addCustomizationServiceForm')

def manage_addCustomizationService(self, id, REQUEST=None):
    """Add a Customization Service.
    """

    site = self.Destination()
    if not ISite.providedBy(site):
        raise BadRequest, "A customization service can only be created in a local site"
    service = CustomizationService(id)
    site._setObject(id, service)
    service = getattr(site, id)
    sm = site.getSiteManager()
    sm.registerUtility(service, interfaces.ICustomizationService)
    add_and_edit(site, id, REQUEST)
    return ''


@silvaconf.subscribe(interfaces.ICustomizationService, IObjectWillBeRemovedEvent)
def unregisterCustomizationService(service, event):
    site = service.aq_parent
    if not ISite.providedBy(site):
        raise ValueError, "Impossible"
    sm = ISite(site).getSiteManager()
    sm.unregisterUtility(service, interfaces.ICustomizationService)

