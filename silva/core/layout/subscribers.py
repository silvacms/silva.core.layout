# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from five import grok
from zope import component
from zope.event import notify
from zope.interface import directlyProvidedBy, directlyProvides
from zope.publisher.browser import SkinChangedEvent
from zope.publisher.interfaces.browser import IBrowserSkinType

from silva.core.layout.interfaces import ISilvaLayer, IMetadata
from silva.core.interfaces import IPublication

from ZPublisher.interfaces import IPubAfterTraversal

try:
    import Products.SilvaLayout
    HAVE_SILVALAYOUT = True
except ImportError:
    HAVE_SILVALAYOUT = False

logger = logging.getLogger('silva.layout')


def applySkinButKeepSome(request, skin):
    logger.debug(u'Setting requested skin %s' % skin.__identifier__)

    # Known interfaces
    ifaces = [iface for iface in directlyProvidedBy(request)
              if not iface.extends(ISilvaLayer)]
    # Add the new skin.
    ifaces.append(skin)
    directlyProvides(request, *ifaces)
    notify(SkinChangedEvent(request))


@grok.subscribe(IPubAfterTraversal)
def publication_after_traversing(event):

    for content in event.request['PARENTS']:
        if not IPublication.providedBy(content):
            continue

        skin_name = IMetadata(content)('silva-layout', 'skin')
        if skin_name:
            # Retrieve the skin object
            skin = component.queryUtility(IBrowserSkinType, name=skin_name)
            if skin is not None:
                # Simply override any previously set skin. We have to
                # do so in order to cover the usecase where we apply
                # only now a skin which is used as a base for a one
                # which was applied on a parent (otherwise we won't
                # see the change, since it's already provided).
                applySkinButKeepSome(event.request, skin)

                if HAVE_SILVALAYOUT:
                    # Set the base url for resources for SilvaLayout
                    event.request.set('resourcebase', content)
                return
            else:
                logger.error('Cannot find requested skin %s' % skin_name)



