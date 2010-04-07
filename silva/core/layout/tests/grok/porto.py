# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
    Development mode is set (see test layer) so the css are not merged together
    
    Grokking the module
    >>> grok('silva.core.layout.tests.grok.porto_fixtures')
    
    Imports
    >>> from zope.interface import alsoProvides
    >>> from zope.component import getMultiAdapter
    >>> from zope.publisher.browser import TestRequest
    >>> from silva.core.layout.tests.grok.porto_fixtures.skin import INewTheme
    
    Initialize a test request and get some content
    >>> request = TestRequest()
    >>> content = self.root
    
    The skin is not registered on the request the adapter lookup should fail
    >>> getMultiAdapter((content, request), name="awesome.html")
    Traceback (most recent call last):
        ...
    ComponentLookupError:...
    
    We register the layer on the request
    >>> alsoProvides(request, INewTheme)
    
    We now ask for a view
    >>> view = getMultiAdapter((content, request), name="awesome.html")
    >>> view
    <silva.core.layout.tests.grok.porto_fixtures.skin.AwesomeView object at ...>
    
    We render it to check that the css is declared
    >>> "style.css" in view()
    True
"""
