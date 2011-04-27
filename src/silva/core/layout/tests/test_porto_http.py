from five import grok
from Products.Silva.testing import TestCase, FunctionalLayer

class PortoHTTPMethodTestCase(TestCase):
    
    layer = FunctionalLayer
    
    def setUp(self):
        self.layer.grok('silva.core.layout.tests.grok.porto_fixtures')
        self.root = self.layer.get_application()
        smb = self.root.service_metadata.getMetadata(self.root)
        smb.setValues('silva-layout', {'skin': "New theme"})
        
    def test_GET(self):
        browser = self.layer.get_browser()
        status = browser.open('/root/awesome.html')
        self.assertEquals(status, 200)
        
    def test_HEAD(self):
        browser = self.layer.get_browser()
        status = browser.open('/root/awesome.html', method='HEAD')
        self.assertEquals(status, 204)

    def test_OPTIONS(self):
        browser = self.layer.get_browser()
        #browser.options.handle_errors = True
        status = browser.open('/root/', method='OPTIONS')
        self.assertEquals(status, 200)
        
        status = browser.open('/root/awesome.html', method='OPTIONS')
        self.assertEquals(status, 204)

    def test_PROPFIND(self):
        browser = self.layer.get_browser()
        browser.options.handle_errors = False
        #baseline for SilvaObject, expect auth requested response
        status = browser.open('/root/', method='PROPFIND')
        self.assertEquals(status, 401)
        
        #what should the SilvaPage do?  proxy to /root/?
        status = browser.open('/root/awesome.html', method='PROPFIND')
        self.assertEquals(status, 401)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PortoHTTPMethodTestCase))
    return suite