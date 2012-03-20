# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IJQueryResources(IDefaultBrowserLayer):
    silvaconf.resource('jquery-1.4.4.min.js')


class IJQueryWaypoints(IJQueryResources):
    """Waypoints are a means to perform an action when an element is
       scrolled to.  Example is keeping an action bar fixed at the top of the
       page once it is scrolled to."""
    silvaconf.resource('waypoints/waypoints.min.js')


class IJQueryUIResources(IJQueryResources):
    silvaconf.resource('jquery-ui-1.8.4.custom.min.js')
    silvaconf.resource('timepicker/jquery.ui.timepicker.js')
    # including this file makes the datepicker chinese
    #silvaconf.resource('jquery-ui-i18n.js')
    silvaconf.resource('jquery-ui-1.8.4.custom.css')
    silvaconf.resource('timepicker/jquery.ui.timepicker.css')
