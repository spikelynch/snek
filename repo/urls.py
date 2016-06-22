from django.conf.urls import url

from . import views

urlpatterns = [
    # /repo/
    url(r'^$',                            views.index,   name='index'),
    # /repo/3
    url(r'^(?P<dataset_id>[0-9]+)/$',     views.dataset, name='dataset'),
    # /repo/fc/${FC_REPO_PATH}
    url(r'^fc/(.*)$',                     views.fc, name='fc')
]
