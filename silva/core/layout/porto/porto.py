# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.cachedescriptors.property import CachedProperty
from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized
from zope.interface import implements
from zope import component

from Products.SilvaLayout.interfaces import IMetadata

from silva.core.views.interfaces import ITemplate, IVirtualSite
from silva.core.views import views as silvaviews


# Main design

class MainTemplate(silvaviews.Template):

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


# # 404 page

# class IErrorPage(ITemplate):
#     pass

# class ErrorPage(MainTemplate):
#     silvaconf.context(INotFound)
#     silvaconf.name('error.html')

#     implements(IErrorPage)

# class ErrorContent(silvaviews.ContentProvider):
#     silvaconf.view(IErrorPage)
#     silvaconf.name('content')

# # Unauthorized page

# class IUnauthorizedPage(ITemplate):
#     pass

# class UnauthorizedPage(MainTemplate):
#     silvaconf.context(IUnauthorized)
#     silvaconf.name('error.html')

#     implements(IUnauthorizedPage)

# class UnauthorizedContent(silvaviews.ContentProvider):
#     silvaconf.view(IUnauthorizedPage)
#     silvaconf.name('content')
