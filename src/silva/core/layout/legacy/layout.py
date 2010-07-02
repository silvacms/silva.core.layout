# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import InitializeClass
import Acquisition

from five import grok
from zope.interface import Interface
from silva.core.layout.legacy.interfaces import ILegacyLayer
from silva.core.views import views as silvaviews

grok.layer(ILegacyLayer)


class LegacyCompatWrapper(Acquisition.Implicit):
    """ Wrapper object to provides compatibility with legacy templates
    """

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, page):
        self.page = page

    security.declareProtected('View', 'view')
    def view(self):
        return self.page.content()


InitializeClass(LegacyCompatWrapper)


def wrap_context(context, view):
    return LegacyCompatWrapper(view).__of__(context.aq_inner)


class LegacyLayout(silvaviews.Layout):
    grok.context(Interface)

    def render(self):
        # We look for templates in ZODB and render it
        is_overrided = hasattr(aq_base(self.context), 'override.html')
        template_name = is_overrided and 'override.html' or 'index_html'
        context = wrap_context(self.context, self.view)
        if not hasattr(context, template_name):
            self.request.setStatus(500)
            return u'<html><body>Legacy layout not available.</body></html>'

        template = getattr(context, template_name)
        return template()


