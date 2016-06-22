from django.forms import ModelForm
from repo.models import Dataset

class DatasetUploadForm(ModelForm):
    class Meta:
        model = Dataset
        fields = [ 'title', 'description', 'dataset' ]

class DatasetForm(ModelForm):
    class Meta:
        model = Dataset
        fields = [ 'title', 'description' ]
