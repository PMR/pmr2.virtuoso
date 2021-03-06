import unittest

import zope.component

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso import engine
from pmr2.virtuoso.interfaces import ISparqlClient
from pmr2.virtuoso.testing.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER


class ClientTestCase(unittest.TestCase):

    layer = PMR2_VIRTUOSO_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        gs = zope.component.getUtility(IPMR2GlobalSettings)
        self.settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')

    def tearDown(self):
        pass

    def test_0000_base(self):
        self.settings.sparql_endpoint = u'http://nohost/sparql'
        client = zope.component.getMultiAdapter((self.portal, self.settings),
            ISparqlClient)
        self.assertEqual(client.portal, self.portal)
        self.assertEqual(client.endpoint, u'http://nohost/sparql')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ClientTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()

