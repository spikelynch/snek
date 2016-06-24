from django.conf.urls import url

from . import views

urlpatterns = [
    # /repo/
#    url(r'^$',                            views.index,   name='index'),
    # /repo/${FC_REPO_PATH}
    url(r'^(.*)$',                         views.fc, name='fc')
]
