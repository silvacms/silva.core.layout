# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.layout.interfaces import ISilvaLayer, ISilvaSkin
from silva.core import conf as silvaconf
from five import grok


class IPorto(ISilvaLayer):
    """A layer from Porto.
    """


class IPortoWithCSS(IPorto):
    """With Silva CSS
    """

    silvaconf.resource('silva.css')


class IPortoSkin(IPortoWithCSS, ISilvaSkin):
    """A skin from Porto.
    """

    grok.skin('Porto')
    silvaconf.resource('porto.css')
