# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IPublicationWorkflow, IAccessSecurity


def settings(browser):
    """Browser settings used to inspect navigation links.
    """
    browser.inspect.add('link', css="div#sidebar a", type='link')


class NavigationTestCase(unittest.TestCase):
    """Test navigation links.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('info', u'Information')
        factory.manage_addMockupVersionedContent('contact', u'Contact')
        factory.manage_addMockupVersionedContent('product', u'Product')
        factory.manage_addMockupVersionedContent('specs', u'Specs')
        IPublicationWorkflow(self.root.info).publish()
        IPublicationWorkflow(self.root.product).publish()
        IAccessSecurity(self.root.product).minimum_role = 'Viewer'
        IAccessSecurity(self.root.specs).minimum_role = 'Editor'

        self.layer.logout()

    def test_public(self):
        """In public, you see the links that are public.
        """
        browser = self.layer.get_browser(settings)

        self.assertEqual(browser.open('http://localhost/root'), 200)
        self.assertEqual(browser.location, '/root')

        # Check for information.
        self.assertEqual(browser.inspect.link, [u'Information'])
        link = browser.inspect.link['information']
        self.assertEqual(link.url, 'http://localhost/root/info')

        browser.login('viewer', 'viewer')
        self.assertEqual(browser.open('http://localhost/root'), 200)

        # As viewer we should see information and product.
        self.assertEqual(browser.inspect.link, [u'Information', u'Product'])
        link = browser.inspect.link['information']
        self.assertEqual(link.url, 'http://localhost/root/info')
        link = browser.inspect.link['product']
        self.assertEqual(link.url, 'http://localhost/root/product')

    def test_preview(self):
        """In preview, we see not yet published content.
        """
        browser = self.layer.get_browser(settings)

        # Access preview. We need to be reader for it.
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 401)

        # Viewer can't see a thing
        browser.login('viewer', 'viewer')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 401)

        # Author should be able to acess
        browser.login('author', 'author')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 200)
        self.assertEqual(browser.location, '/root/++preview++')

        # We should see information, contact and product.
        self.assertEqual(
            browser.inspect.link,
            [u'Information', u'contact', u'Product'])
        link = browser.inspect.link['information']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/info')
        link = browser.inspect.link['contact']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/contact')
        link = browser.inspect.link['product']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/product')

        # Chief editor can see more.
        browser.login('chiefeditor', 'chiefeditor')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 200)
        self.assertEqual(browser.location, '/root/++preview++')

        self.assertEqual(
            browser.inspect.link,
            [u'Information', u'contact', u'Product', u'specs'])
        link = browser.inspect.link['information']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/info')
        link = browser.inspect.link['contact']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/contact')
        link = browser.inspect.link['product']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/product')
        link = browser.inspect.link['specs']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/specs')



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NavigationTestCase))
    return suite
