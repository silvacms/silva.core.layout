import Acquisition
from silva.core.views import views as silvaviews

class LegacyCompatContext(Acquisition.Implicit):
    """ Wrapper object to provides compatibility with legacy templates
    """

    def __init__(self, context, page):
        super(LegacyCompatContext, self).__init__()
        self.context = wrapped_context
        self.page = page

    def view(self):
        return self.page.content()


class LegacyLayout(silvaviews.Layout):

    def default_namespace(self):
        namespace = super(LegacyLayout, self).default_namespace()
        namespace['context'] = LegacyCompatContext(self.context, self.view)
        return namespace


