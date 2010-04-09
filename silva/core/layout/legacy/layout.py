from five import grok
from zope.interface import Interface
import Acquisition
from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from silva.core.views import views as silvaviews
from silva.core.layout.legacy.interfaces import ILegacyLayer
from silva.core.interfaces import ISilvaObject

grok.layer(ILegacyLayer)


class LegacyCompatWrapper(Acquisition.Implicit):
    """ Wrapper object to provides compatibility with legacy templates
    """

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, page):
        self.page = page

    security.declareProtected('View', 'view')
    def view(self):
        return self.page.content()


InitializeClass(LegacyCompatWrapper)

def wrap_context(context, view):
    return LegacyCompatWrapper(view).__of__(context.aq_inner)


class LegacyLayout(silvaviews.Layout):
    grok.context(ISilvaObject)

    def render(self):
        template = getattr(
            wrap_context(self.context, self.view),
            'index_html')
        return template()


