from silva.core import conf as silvaconf
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IJQueryResources(IDefaultBrowserLayer):
    silvaconf.resource('jquery-1.4.2.min.js')
    silvaconf.resource('jquery-ui-1.8.4.custom.min.js')
    silvaconf.resource('jquery-ui-i18n.js')
    silvaconf.resource('jquery-ui-1.8.4.custom.css')
