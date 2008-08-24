# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.layout.interfaces import ISilvaLayer, ISilvaSkin
from silva.core import conf as silvaconf

class IPorto(ISilvaLayer):
    """A layer from Porto.
    """

    silvaconf.resource('silva.css')
    silvaconf.resource('porto.css')

class IPortoSkin(IPorto, ISilvaSkin):
    """A skin from Porto.
    """

    silvaconf.skin('Porto')
    
