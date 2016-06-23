from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging

from .forms import DatasetUploadForm
from .models import Dataset

import fcrepo4

from rdflib import Literal, URIRef
from rdflib.namespace import DC, Namespace
import re

NAMESPACES = {
    'ldp':  re.compile(r'^http://www.w3.org/ns/ldp#(.*)$'),
    'dc':   re.compile(r'^http://purl.org/dc/terms/(.*)$'),
    'pdcm': re.compile(r'^http://pcdm.org/models#(.*)$')
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

    t = { 'path': fcpath, 'uri': uri }

    namespaces = {}
    if not hasattr(resource, 'rdf'):
        t['binary'] = resource.uri
        t['image'] = 1
    else:
        # extract RDF into dicts with p, o, p_label, o_label
        t['debug'] = resource.rdf.serialize(format="nt")
        for s, p, o in resource.rdf:
            for abbrev, re in NAMESPACES.items():
                m = re.match(str(p))
                if m:
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
def index(request):
    if request.method == 'POST':
        logger.warn("Got to the post part")
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            logger.warn("Form is valid")
            dataset = form.save(commit=False)
            dataset.user = request.user
            dataset.content_type = request.FILES['dataset'].content_type
            dataset.save()
#            table = ImageTable(dataset)
#            table.save()
            return HttpResponseRedirect('/repo/%d' % dataset.id)
        else:
            logger.warn("Form is invalid")
    else:
        form = DatasetUploadForm()

    datasets = Dataset.objects.filter(user=request.user)
    return render(request, 'repo/index.html', { 'datasets': datasets, 'form': form })






@login_required()
def dataset(request, dataset_id):
    ds = Dataset.objects.get(pk=dataset_id)
    if ds:
        return render(request, 'repo/dataset.html', { 'dataset': ds })
    else:
        return HttpResponseNotFound('<h1>Dataset not found</h1>')

@login_required()
def databytes(request, dataset_id):
    logger.warn("databytes: %s" % request.path)
    ds = Dataset.objects.get(pk=dataset_id)
    content_type = ds.content_type
    if ds:
        response = HttpResponse(content_type=content_type)
        response['Content-disposition'] = 'attachment;filename="%s"' % ds.dataset.url
        with ds.dataset.file as f:
            response.write(f.read())
        return response
    else:
        return HttpResponseNotFound('<h1>Dataset not found</h1>')

    
def json(request, dataset_id):
    """This runs a query over a dataset and returns the requested fields"""
    ds = Dataset.objects.get(pk=dataset_id)
    expr = request.GET.get('query')
    if ds:
#        table = ImageTable(ds)
#        if table:
#            json = table.json(expr)
#        else:
#            json = { 'error': 'system error' }
        return HttpResponse(json, content_type="application/json")
    else:
        return HttpResponseNotFound('<h1>Dataset not found</h1>')
