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


class Content(silvaviews.ContentProvider):

    def render(self):
        return self.context.view()


class Breadcrumbs(silvaviews.ContentProvider):
    pass


