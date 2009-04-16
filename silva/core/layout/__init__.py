# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.ExtensionRegistry import extensionRegistry
from silva.core.conf.installer import DefaultInstaller
import zope.interface


class IExtension(zope.interface.Interface):
    """silva.core.layout extension.
    """

class CoreLayoutInstaller(DefaultInstaller):
    __name__ = "silva.core.layout.install"

install = CoreLayoutInstaller('Silva Core Layout', IExtension)


def initialize(context):
    extensionRegistry.register(
        'Silva Core Layout', 'Silva 2.2 Layout system compatiblity',
        context, [], install, depends_on=('Silva', 'SilvaLayout',),)
