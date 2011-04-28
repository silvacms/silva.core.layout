# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized

from silva.core.layout.interfaces import ICustomizableLayer
from silva.core.views import views as silvaviews
from silva.core.interfaces import INotViewable, INoDefaultDocument

grok.layer(ICustomizableLayer)


# 404 page

class ErrorPage(silvaviews.Page):
    grok.context(INotFound)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(404)


# Unauthorized page

class UnauthorizedPage(silvaviews.Page):
    grok.context(IUnauthorized)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(401)
        self.response.setHeader('WWW-Authenticate', 'basic realm="Zope"')

class NotViewablePage(silvaviews.Page):
    grok.context(INotViewable)
    grok.name('error.html')
    
    def update(self):
        """the apache book states for code 409:
        409: Conflict: the request could not be completed because of a conflict
            with the current state of the resource
            This seems to be the closest 4XX code to match this condition.  In other
            words, the "state of this resource" is that it is unpublished, which is 
            in conflict with the request to serve the published version of the
            resource.
        """
        self.response.setStatus(409)
        
class NoDefaultDocumentPage(silvaviews.Page):
    grok.context(INoDefaultDocument)
    grok.name('error.html')
    
    def update(self):
        self.response.setStatus(403)

# Other error

class OtherErrorPage(silvaviews.Page):
    grok.context(Exception)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(500)
