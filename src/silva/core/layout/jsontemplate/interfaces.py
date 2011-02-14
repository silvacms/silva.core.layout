# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IJsonTemplateResources(IDefaultBrowserLayer):
    silvaconf.resource('json-template.js')
