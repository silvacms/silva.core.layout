# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IAccessSecurity


class PageTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('contact', u'Contact')

    def test_public_page(self):
        assert False, 'TBD'

    def test_restricted_page(self):
        assert False, 'TBD'

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PageTestCase))
    return suite
