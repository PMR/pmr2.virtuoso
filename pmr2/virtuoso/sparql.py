import urllib
from urlparse import urljoin
import rdflib

import pmr2.rdf

iri_replacements = {
    rdflib.URIRef(''): rdflib.URIRef('#'),
}

def quote_iri(url):
    return urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")

def n3(item):
    # handle special cases
    return iri_replacements.get(item, item).n3()

def n3_insert(graph, subject_prefix=None):
    for s, p, o in graph.triples((None, None, None)):
        if subject_prefix:
            s = rdflib.URIRef(urljoin(subject_prefix, s))
        yield u'%s %s %s .' % (n3(s), n3(p), n3(o))

def insert(graph, graph_iri, subject_prefix=None):
    """
    Generate an insert statement based on the graph object and iri.
    """

    return (
        'INSERT INTO <%s> {\n'
        '    %s\n'
        '}' % (
            quote_iri(graph_iri),
            '\n'.join(n3_insert(graph, subject_prefix)),
        )
    )

def clear(graph_iri):
    """
    Generate a clear graph statement on the iri.
    """

    return 'CLEAR GRAPH <%s>' % (quote_iri(graph_iri))
