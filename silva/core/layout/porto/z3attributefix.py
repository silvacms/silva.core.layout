# Fixes for the z3attributes 'edit' object on 2.1. On 2.2 this thing
# is in the SMILayout, so no error there.

from Products.Silva.SilvaObject import Zope3ViewAttribute

from silva.core.views import views as silvaviews
from five import grok

from interfaces import IPorto

grok.layer(IPorto)

class MainLayout(silvaviews.Layout):
    grok.template('mainlayout')
    grok.context(Zope3ViewAttribute)

