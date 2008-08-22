# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.component import getGlobalSiteManager
from zope.component import getUtility, getUtilitiesFor
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

from Products.Silva.BaseService import SilvaService
from Products.Silva.helpers import add_and_edit
from Products.Silva.interfaces import ISilvaObject

from silva.core import conf as silvaconf
from silva.core.views.ttwtemplates import TTWViewTemplate
from silva.core.views.interfaces import ITemplate, ICustomizedTemplate
from silva.core.views import views as silvaviews

from interfaces import ICustomizableType, ILayerType, ICustomizable
from interfaces import ICustomizableMarker

from utils import findSite, findNextSite

class CustomizationService(Folder, SilvaService):

    meta_type = 'Silva Customization Service'

    silvaconf.icon('customization.png')
    silvaconf.factory('manage_addCustomizationServiceForm')
    silvaconf.factory('manage_addCustomizationService')

    manage_options = (
        {'label':'Customize', 'action':'manage_customization'},
        ) + Folder.manage_options


class CustomizationManagementView(silvaviews.ZMIView):

    silvaconf.context(CustomizationService)
    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.baseclass()

    interface = None
    layer = None

    def availablesInterfaces(self, extra=None):
        """Return available interfaces starting from base.
        """
        base = self.interface
        if base is None:
            base = ICustomizable

        def predicat(value):
            return value.isOrExtends(base) or (extra and value.isOrExtends(extra))

        interfaces = getUtilitiesFor(ICustomizableType, context=self.context)
        return sorted([name for name, interface in interfaces if predicat(interface)])

    def availablesInterfacesAndMarkers(self):
        """Return available interfaces starting from base and markers.
        """
        return self.availablesInterfaces(extra=ICustomizableMarker)

    def availablesLayers(self):
        """Return available layers starting from base.
        """
        base = self.layer
        if base is None:
            base = IDefaultBrowserLayer
        layers = getUtilitiesFor(ILayerType)
        return sorted([name for name, layer in layers if layer.isOrExtends(base)])


def getViews(where, interface, layer):
    """Get all view registrations for a particular interface.
    """
    
    def viewsFor(sm, name):
        for reg in sm.registeredAdapters():
            if (len(reg.required) == 2 and
                interface.isOrExtends(reg.required[0]) and
                reg.required[0].isOrExtends(ICustomizable) and
                reg.required[1].isOrExtends(layer)):
                yield (reg, name)

    site = findNextSite(where)
    views = []
    while not (site is None):
        views.extend(viewsFor(site.getSiteManager(), u'/'.join(site.getPhysicalPath())))
        site = findNextSite(site)
    views.extend(viewsFor(getGlobalSiteManager(), u'Global'))
    return views


def isAFiveTemplate(factory):
    """There is no interfaces for Five templates. That's the hack to
    guess it's an five template.
    """
    return (hasattr(factory, '__name__') and factory.__name__.startswith('SimpleViewClass'))

class ManageCustomTemplates(CustomizationManagementView):

    silvaconf.name('manage_customization')

    def update(self):
        self.availableTemplates = []
        self.selectedInterface = self.request.form.get('interface', None)
        self.selectedLayer = self.request.form.get('layer', IDefaultBrowserLayer.__identifier__)

        if self.selectedInterface:

            interface = getUtility(ICustomizableType, name=self.selectedInterface)
            layer = getUtility(ILayerType, name=self.selectedLayer)
            absolute_url = self.context.absolute_url()
            templates = getViews(self.context, interface, layer)

            for reg, origin in sorted(templates, key=lambda r: r[0].name):
                customizable = True
                link = False
                if ITemplate.implementedBy(reg.factory):
                    if hasattr(reg.factory, 'template'):
                        template = reg.factory.template._template.filename
                    else:
                        template = u'direct rendering'
                        customizable = False
                    config = u'Grok page template'
                elif ICustomizedTemplate.providedBy(reg.factory):
                    template = absolute_url + '/' + reg.factory.id + '/manage_workspace'
                    config = u'Customized page template'
                    link = reg.factory.id
                    customizable = False
                elif isAFiveTemplate(reg.factory):
                    template = reg.factory.index.filename
                    config = reg.info.file
                else:           # Unknown view type.
                    continue
                self.availableTemplates.append({
                        'name': reg.name,
                        'for': reg.required[0].__identifier__,
                        'layer': reg.required[1].__identifier__,
                        'template': template,
                        'config': config,
                        'origin': origin,
                        'customizable': customizable,
                        'link': link
                        })
        else:
            self.selectedInterface = ISilvaObject.__identifier__
        

class ManageViewTemplate(CustomizationManagementView):

    silvaconf.name('manage_template')

    def update(self):
        assert 'for' in self.request.form
        assert 'name' in self.request.form

        self.name = self.request.form['name']
        self.origin = self.request.form['origin']
        self.layer = getUtility(ILayerType, self.request.form['layer'])
        self.interface = getUtility(ICustomizableType, name=self.request.form['for'])

        view = None
        for reg, origin in getViews(self.context, self.interface, self.layer):
            if origin != self.origin:
                continue
            if (reg.name == self.name and 
                reg.required[0] == self.interface and
                reg.required[1] == self.layer):
                view = reg
                break
        if view is None:
            raise ValueError, 'Template not found'

        self.reg = reg
        self.factory = reg.factory
        if ITemplate.implementedBy(reg.factory):
            self.code = open(self.factory.template._template.filename, 'rb').read()
        else:
            self.code = open(self.factory.index.filename, 'rb').read()


class ManageCreateCustomTemplate(ManageViewTemplate):

    silvaconf.name('manage_createCustom')


    def permission(self):
        permissions = self.factory.__ac_permissions__
        for permission, methods in permissions:
            if methods[0] in ('', '__call__',):
                return permission

    def update(self):
        super(ManageCreateCustomTemplate, self).update()

        for_name = self.request.form['customize_for']
        layer_name = self.request.form['customize_layer']
        customize_for = getUtility(ICustomizableType, name=for_name)
        customize_layer = getUtility(ILayerType, name=layer_name)
        
        template_id = '%s-%s-%s' % (for_name.split('.')[-1],
                                    layer_name.split('.')[-1],
                                    self.name)

        viewclass = self.factory.__bases__[0]
        permission = self.permission()

        new_template = TTWViewTemplate(template_id, self.code, 
                                       view=viewclass, permission=permission)
        
        self.context._setObject(template_id, new_template)

        manager = findSite(self.context).getSiteManager()
        manager.registerAdapter(new_template, required=(customize_for, customize_layer,),
                                provided=self.reg.provided, name=self.name)

        new_template = getattr(self.context, template_id)
        self.redirect(new_template.absolute_url() + '/manage_workspace')

                                       
    def render(self):
        return u'Customized.'


manage_addCustomizationServiceForm = PageTemplateFile(
    "www/customizationServiceAdd", globals(),
    __name__='manage_addCustomizationServiceForm')

def manage_addCustomizationService(self, id, REQUEST=None):
    """Add a Customization Service.
    """

    service = CustomizationService(id)
    self._setObject(id, service)
    add_and_edit(self, id, REQUEST)
    return ''
