import unittest
import doctest

from Testing import ZopeTestCase
from Testing.ZopeTestCase.zopedoctest.functional import http
from pkg_resources import resource_listdir
from silva.resourceinclude.testing import ResourceIncludeLayer
from zope.interface.verify import verifyObject
import five.grok.testing


extraglobs = {'verifyObject': verifyObject,
              'browser': http(),
              'grok': five.grok.testing.grok,}


def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'silva.core.layout.tests.%s.%s' % (name, filename[:-3])
        test = ZopeTestCase.FunctionalDocTestSuite(
            dottedname,
            extraglobs=extraglobs,
            optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)

        test.layer = ResourceIncludeLayer
        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suiteFromPackage('grok'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
