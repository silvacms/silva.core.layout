# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.interfaces import IVersionedContent
from silva.core.layout.interfaces import ISilvaLayer
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IView
from silva.translations import translate as _
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.i18n import translate

from AccessControl import Unauthorized
from AccessControl.security import checkPermission
from zExceptions import NotFound

grok.layer(ISilvaLayer)


class FallbackLayout(silvaviews.Layout):
    """ Layout for objects that do not provide ISilvaObject
    """
    grok.context(Interface)

    def render(self):
        return """
            <html>
                <head><!-- no layout --></head>
                <body>%s</body>
            </html>
        """ % self.view.content()


class MainPage(silvaviews.Page):
    grok.name('index.html')

    def render(self):
        view = queryMultiAdapter(
            (self.context, self.request), name='content.html')
        if view is None:
            raise NotFound('content.html')
        if IView.providedBy(view):
            if view.content is None:
                msg = _('Sorry, this ${meta_type} is not viewable.',
                        mapping={'meta_type': self.context.meta_type})
                return '<p>%s</p>' % translate(msg, context=self.request)
        return view()


class VersionedContentMainPage(silvaviews.Page):
    grok.name('index.html')
    grok.context(IVersionedContent)

    def render(self):
        view = queryMultiAdapter(
            (self.context, self.request), name='content.html')
        if view is None:
            raise NotFound('content.html')
        if IView.providedBy(view):
            version_name = self.request.other.get(
                'SILVA_PREVIEW_NAME', None)
            if version_name is not None:
                if not checkPermission('silva.ReadSilvaContent', self.context):
                    raise Unauthorized(
                        "You need to be authenticated to access this version")
                view.content = self.context._getOb(version_name, None)
            if view.content is None:
                msg = _('Sorry, this ${meta_type} is not viewable.',
                        mapping={'meta_type': self.contex.tmeta_type})
                return '<p>%s</p>' % translate(msg, context=self.request)
        return view()


