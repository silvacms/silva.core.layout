# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.cachedescriptors.property import CachedProperty
from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized
from zope.traversing.browser import absoluteURL
from zope import component, interface

from silva.core.interfaces import IContainer
from Products.SilvaLayout.interfaces import IMetadata

from silva.core.views.interfaces import IVirtualSite
from silva.core.views import views as silvaviews
from five import grok

from interfaces import IPorto

grok.layer(IPorto)

# Main design

class MainLayout(silvaviews.Layout):

    grok.template('mainlayout')

    @CachedProperty
    def metadata(self):
        return IMetadata(self.context)

    @CachedProperty
    def root(self):
        virtual_site = component.getMultiAdapter(
            (self.context, self.request), IVirtualSite)
        return virtual_site.get_root()

    @CachedProperty
    def root_url(self):
        return self.root.absolute_url()


class MainTemplate(silvaviews.Template):

    grok.name('index.html')

    def render(self):
        return self.context.view()


class Layout(silvaviews.ContentProvider):
    """Layout of the page.
    """
    pass


class Header(silvaviews.ContentProvider):
    """Define a site header.
    """
    pass


class Breadcrumbs(silvaviews.ContentProvider):
    """Breadcrumbs.
    """
    pass


class Navigation(silvaviews.ContentProvider):
    """Navigation
    """

    @CachedProperty
    def filter_service(self):
        # Should be an utility
        return self.context.service_toc_filter

    def filter_entries(self, nodes):
        return filter(lambda node: not self.filter_service.filter(node), nodes)

    @CachedProperty
    def navigation_current(self):
        return self.context.aq_base

    def navigation_entries(self, node, depth=0, maxdepth=2):
        info = {'url': absoluteURL(node, self.request),
                'title': node.get_title_or_id(),
                'nodes': None,
                'onbranch': node in self.request.PARENTS,
                'current': node.aq_base is self.navigation_current}
        if depth < maxdepth and IContainer.providedBy(node):
            children = self.filter_entries(node.get_ordered_publishables())
            info['nodes'] = list(children)
        return info

    @CachedProperty
    def navigation_root(self):
        node = self.context.get_publication()
        return list(self.filter_entries(node.get_ordered_publishables()))


class Footer(silvaviews.ContentProvider):
    """Site footer.
    """
    pass


# 404 page

class ErrorPage(silvaviews.Template):
    grok.context(INotFound)
    grok.name('error.html')


# Unauthorized page

class UnauthorizedPage(silvaviews.Template):
    grok.context(IUnauthorized)
    grok.name('error.html')

# Other error

class OtherErrorPage(silvaviews.Template):
    grok.context(interface.Interface)
    grok.name('error.html')
