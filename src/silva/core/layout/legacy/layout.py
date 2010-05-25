# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
import Acquisition

from five import grok
from silva.core.interfaces import ISilvaObject
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
    grok.context(ISilvaObject)

    def render(self):
        template = getattr(
            wrap_context(self.context, self.view),
            'index_html')
        return template()


