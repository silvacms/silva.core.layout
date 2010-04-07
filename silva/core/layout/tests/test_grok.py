from Products.Silva.tests.test_grok import suiteFromPackage
from Products.Silva.tests.layer import SilvaLayer
import unittest
import Globals


class ResourceIncludeLayer(SilvaLayer):
    @classmethod
    def setUp(self):
        self.previous_dev_mode = Globals.DevelopmentMode
        Globals.DevelopmentMode = True

    @classmethod
    def tearDown(self):
        Globals.DevelopmentMode = self.previous_dev_mode


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suiteFromPackage('grok', 'silva.core.layout.tests',
        layer=ResourceIncludeLayer))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
