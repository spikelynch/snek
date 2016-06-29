from django.conf.urls import url

from . import views

urlpatterns = [
    # /repo/search?q=${QUERY}
    url(r'^search',                        views.search, name='search'),
    # /repo/${FC_REPO_PATH}
    url(r'^(.*)$',                         views.fc, name='fc')
]
