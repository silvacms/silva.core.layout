# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.interface import implementedBy, providedBy, Interface
from zope import component


def queryAdapterOnClass(klass, interface=None, name=u''):
    """Query an adapter on a klass instead of an instead of it.
    """
    sm = component.getGlobalSiteManager()
    required = implementedBy(klass)
    factory = sm.adapters.lookup((required,), interface, name)
    if factory is not None:
        result = factory(klass)
        if result is not None:
            return result
    return None

def queryMultiAdapterWithInterface(adapts, obj, interface=None, name=u""):
    """Query a multiple adapter, where the first is already an
    interface. You have to provides the object you want to replace the
    interface when the adapter is build.
    """
    sm = component.getGlobalSiteManager()
    adapts = list(adapts)
    required = [adapts[0], ] + [providedBy(k) for k in adapts[1:]]
    if interface is None:
        interface = Interface
    factory = sm.adapters.lookup(required, interface, name)
    if factory is not None:
        args = [obj, ] + adapts[1:]
        result = factory(*args)
        if result is not None:
            return result
    return None
