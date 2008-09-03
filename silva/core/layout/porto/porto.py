# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

from interfaces import IPorto

silvaconf.layer(IPorto)

class MainTemplate(silvaviews.Template):

    silvaconf.name('index.html')


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

