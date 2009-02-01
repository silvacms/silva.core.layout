# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.cachedescriptors.property import CachedProperty
from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized
from zope.interface import implements

from Products.SilvaLayout.interfaces import IMetadata
from Products.Silva.interfaces import IVirtualHosting

from silva.core.views.interfaces import ITemplate
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

from interfaces import IPorto

silvaconf.layer(IPorto)

# Main design

class MainTemplate(silvaviews.Template):

    silvaconf.name('index.html')
    silvaconf.template('maintemplate')

    @CachedProperty
    def metadata(self):
        return IMetadata(self.context)

    @CachedProperty
    def root(self):
        return IVirtualHosting(self.context).getSilvaOrVirtualRoot()

    @CachedProperty
    def root_url(self):
        return self.root.absolute_url()


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


class Content(silvaviews.ContentProvider):
    """Content of the page.
    """

    def render(self):
        return self.context.view()


class Footer(silvaviews.ContentProvider):
    """Site footer.
    """
    pass


# 404 page

class IErrorPage(ITemplate):
    pass

class ErrorPage(MainTemplate):
    silvaconf.context(INotFound)
    silvaconf.name('error.html')

    implements(IErrorPage)

class ErrorContent(silvaviews.ContentProvider):
    silvaconf.view(IErrorPage)
    silvaconf.name('content')

# Unauthorized page

class IUnauthorizedPage(ITemplate):
    pass

class UnauthorizedPage(MainTemplate):
    silvaconf.context(IUnauthorized)
    silvaconf.name('error.html')

    implements(IUnauthorizedPage)

class UnauthorizedContent(silvaviews.ContentProvider):
    silvaconf.view(IUnauthorizedPage)
    silvaconf.name('content')
