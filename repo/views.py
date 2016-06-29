from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import logging, requests, json

from .forms import DatasetUploadForm
from .models import Dataset

import fcrepo4

from rdflib import Literal, URIRef
from rdflib.namespace import DC, Namespace
import re

NAMESPACES = {
    'ldp':  re.compile(r'^http://www.w3.org/ns/ldp#(.*)$'),
    'dc':   re.compile(r'^http://purl.org/dc/.*?/([^/]*)$'),
    'pdcm': re.compile(r'^http://pcdm.org/models#(.*)$'),
    'fedora': re.compile(r'^http://fedora.info/definitions/v4/repository#(.*)$'),
    }


logger = logging.getLogger(__name__)


@login_required()
def fc(request, fcpath):
    repo = fcrepo4.Repository(config=settings.FCREPO)
    if fcpath and fcpath[-1] == '/':
        uri = repo.path2uri(fcpath)
    else:
        uri = repo.path2uri(fcpath + '/')
    try:
        resource = repo.get(uri)
    except fcrepo4.ResourceError as e:
        return HttpResponseNotFound('<h1>Resource not found</h1>')

    if request.method == 'POST':
        return upload(request, resource)
    t = { 'path': fcpath, 'uri': uri, 'form': DatasetUploadForm() }

    namespaces = {}
    if not hasattr(resource, 'rdf'):
        t['binary'] = resource.uri
        t['image'] = 1
    else:
        # extract RDF into dicts with p, o, p_label, o_label
        t['turtle'] = resource.rdf.serialize(format="turtle")
        for s, p, o in resource.rdf:
            logger.warn("Predicate: {}".format(str(p)))
            for abbrev, re in NAMESPACES.items():
                m = re.match(str(p))
                if m:
                    logger.warn("Matched {}".format(abbrev))
                    field = m.group(1)
                    v = {
                        'p': p,
                        'o': o,
                        'p_label': field,
                        'o_label': str(o)
                        }
                    if type(o) == URIRef:
                        v['url'] = o
                    if abbrev not in namespaces:
                        namespaces[abbrev] = {}
                    if field not in namespaces[abbrev]:
                        namespaces[abbrev][field] = [ v ]
                    else:
                        namespaces[abbrev][field].append(v)
    t['rdf'] = namespaces
    if 'dc' in namespaces:
        for field in [ 'title', 'creator', 'description' ]:
            if field in namespaces['dc']:
                t[field] = namespaces['dc'][field][0]['o_label']
    return render(request, 'repo/resource.html', t)




@login_required()
def upload(request, resource):
    form = DatasetUploadForm(request.POST, request.FILES)
    if form.is_valid():
        upload = request.FILES['dataset']
        dataset = form.save(commit=False)
        dataset.user = request.user
        dataset.content_type = upload.content_type
        dataset.save()
        dc = resource.repo.dc_rdf({
            'title': dataset.title,
            'description': dataset.description,
            'creator': dataset.user
            }
            )
        try:
            container = resource.add_container(dc, slug=upload.name)
        except fcrepo4.ResourceError as e:
            em = "FC4 resource error: {} {} {}".format(e.status_code, e.reason, e.message)
            logger.error(em)
            messages.error(request, em)
            return HttpResponseRedirect(request.path)
        binary = container.add_binary(upload.chunks(), slug=upload.name, mime=upload.content_type)
        messages.info(request, "Added new binary in a container at {}".format(container.uri))
        return HttpResponseRedirect(request.path)
    else:
        logger.warn("Form is invalid")
    return render(request, 'repo/resource.html', {'form': form })



@login_required()
def search(request):
    q = request.GET.get('q', None)
    if not q:
        return HttpResponseRedirect('repo/')
    else:
        solr_uri = settings.FCREPO['solr_uri']
        solrq = "title:*{}* OR description:*{}* OR author:{}".format(q, q, q)
        params = {}
        params['q'] = solrq
        params['wt'] = 'json'
        vars = {}
        r = requests.get(solr_uri, params=params)
        if r.status_code == requests.codes.ok:
            response = json.loads(r.text)['response']
            vars['num'] = response['numFound']
            vars['docs'] = response['docs']
            logger.warn("results = {}".format(response))
        else:
            vars['error'] = "Solr error: {} {}".format(r.status_code, r.reason)
            logger.error(error)
        return render(request, 'repo/search.html', vars)




