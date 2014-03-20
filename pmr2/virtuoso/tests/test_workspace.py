import unittest

import zope.component
import zope.interface

from Zope2.App import zcml
from Products.Five import fiveconfigure

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.interfaces import IWorkspaceRDFInfo
from pmr2.virtuoso.interfaces import IWorkspaceRDFIndexer
from pmr2.virtuoso.workspace import WorkspaceRDFInfo

from pmr2.virtuoso.tests import base
from pmr2.virtuoso.browser.workspace import WorkspaceRDFInfoEditForm

from pmr2.testing.base import TestRequest


class WorkspaceAnnotationTestCase(base.WorkspaceRDFTestCase):

    def test_workspace_rdf_annotation(self):
        rdfinfo = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFInfo)

        self.assertTrue(isinstance(rdfinfo, WorkspaceRDFInfo))

    def test_workspace_rdf_indexer(self):
        rdfinfo = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFInfo)

        rdfinfo.paths = ['simple.rdf', 'special_cases.xml']

        indexer = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFIndexer)

        results = list(indexer.sparql_generator('urn:test:'))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0],
            'CLEAR GRAPH <urn:test:/plone/workspace/virtuoso_test>')

        self.assertEqual(' '.join(results[1].split()),
            u'INSERT INTO <urn:test:/plone/workspace/virtuoso_test> { '
                '<#test> <http://purl.org/dc/elements/1.1/title> "Test Node" .'
            ' }')

    def test_workspace_double_format(self):
        rdfinfo = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFInfo)

        rdfinfo.paths = ['simple.rdf', 'simple.n3']

        indexer = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFIndexer)

        results = list(indexer.sparql_generator('urn:test:'))

        self.assertEqual(' '.join(results[1].split()),
            u'INSERT INTO <urn:test:/plone/workspace/virtuoso_test> { '
                '<#test> <http://purl.org/dc/elements/1.1/title> "Test Node" .'
            ' }')

        self.assertEqual(' '.join(results[2].split()),
            u'INSERT INTO <urn:test:/plone/workspace/virtuoso_test> { '
                '<#test> <http://purl.org/dc/elements/1.1/title> "Test Node" .'
            ' }')

        # how virtuoso handles this (or how should) is undefined.


class WorkspaceBrowserTestCase(base.WorkspaceRDFTestCase):
    """
    For the browser side of things.
    """

    def test_workspace_rdf_edit_form_render(self):
        context = self.portal.workspace['virtuoso_test']
        request = TestRequest()
        form = WorkspaceRDFInfoEditForm(context, request)
        result = form()
        self.assertIn('RDF Paths', result)
        self.assertIn('simple.rdf', result)
        self.assertIn('special_cases.xml', result)
        self.assertIn('form.buttons.apply', result)

    def test_workspace_rdf_edit_form_submit(self):
        context = self.portal.workspace['virtuoso_test']
        rdfinfo = zope.component.getAdapter(context, IWorkspaceRDFInfo)
        self.assertIsNone(rdfinfo.paths)

        request = TestRequest(form={
            'form.widgets.paths': ['simple.rdf', 'special_cases.xml'],
            'form.buttons.apply': 1,
        })
        form = WorkspaceRDFInfoEditForm(context, request)
        form.update()

        self.assertEqual(rdfinfo.paths, ['simple.rdf', 'special_cases.xml'])

    def test_workspace_rdf_edit_form_export(self):
        context = self.portal.workspace['virtuoso_test']
        rdfinfo = zope.component.getAdapter(
            self.portal.workspace['virtuoso_test'], IWorkspaceRDFInfo)
        rdfinfo.paths = ['simple.rdf', 'special_cases.xml']

        request = TestRequest(form={
            'form.widgets.paths': ['simple.rdf'],
            'form.buttons.export_rdf': 1,
        })
        form = WorkspaceRDFInfoEditForm(context, request)
        form.update()

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        engine = zope.component.getAdapter(settings, IEngine)

        self.assertEqual(len(engine.stmts), 2)
        self.assertEqual(engine.stmts[0], 'SPARQL '
            'CLEAR GRAPH <urn:pmr:virtuoso:/plone/workspace/virtuoso_test>')
