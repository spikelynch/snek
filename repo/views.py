from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required

import logging

from .forms import DatasetUploadForm
from .models import Dataset


logger = logging.getLogger(__name__)


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
