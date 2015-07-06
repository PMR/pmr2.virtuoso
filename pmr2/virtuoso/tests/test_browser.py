import unittest

import zope.component
from plone.testing.z2 import Browser

from Products.CMFCore.utils import getToolByName

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.browser.client import SparqlClientForm
from pmr2.virtuoso.interfaces import ISparqlClient
from pmr2.virtuoso.interfaces import ISettings
from pmr2.virtuoso.testing.layer import PMR2_VIRTUOSO_INTEGRATION_LAYER


class ClientBrowserTestCase(unittest.TestCase):

    layer = PMR2_VIRTUOSO_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['portal'].REQUEST

        self.testbrowser = Browser(self.layer['portal'])

    def test_0000_form_render(self):
        form = SparqlClientForm(self.portal, self.request)
        results = form()
        self.assertIn('Execute', results)

    def test_0100_form_submit(self):
        # doesn't matter what these are, as we use dummy values, as long
        # as the graph var is determined.
        self.request.form['form.widgets.statement'] = \
            'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'
        self.request.form['form.buttons.execute'] = 1
        self.request.method = 'POST'
        form = SparqlClientForm(self.portal, self.request)
        form.disableAuthenticator = True
        results = form()
        self.assertEqual(
            len(results.split('http://nohost/plone/workspace/virtuoso_test')),
            5) # 4 of these in total.
        self.assertIn('http://example.com/object', results)
        self.assertNotIn('urn:pmr:virtuoso:/plone/workspace/no_permission',
            results)

    def test_0101_browser_submit_noperm(self):
        portal_url = self.portal.absolute_url()
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search')
        self.testbrowser.getControl(name='form.widgets.statement').value = \
            'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'
        self.testbrowser.getControl(name='form.buttons.execute').click()
        results = self.testbrowser.contents
        self.assertEqual(
            len(results.split('http://nohost/plone/workspace/virtuoso_test')),
            1) # nothing for now, no permission

    def test_0102_browser_submit(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        wft = getToolByName(self.portal, 'portal_workflow')
        wft.doActionFor(self.portal.workspace.virtuoso_test, 'publish')
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        # Force a commit to make things work.
        self.portal.workspace.virtuoso_test.reindexObject()
        import transaction
        transaction.commit()

        portal_url = self.portal.absolute_url()
        self.testbrowser.open(portal_url + '/pmr2_virtuoso_search')
        self.testbrowser.getControl(name='form.widgets.statement').value = \
            'SELECT ?_g ?s ?p ?o WHERE { GRAPH ?_g { ?s ?p ?o } }'
        self.testbrowser.getControl(name='form.buttons.execute').click()
        results = self.testbrowser.contents
        self.assertEqual(
            len(results.split('http://nohost/plone/workspace/virtuoso_test')),
            5)
        self.assertIn('http://example.com/object', results)
        self.assertNotIn('urn:pmr:virtuoso:/plone/workspace/no_permission',
            results)
