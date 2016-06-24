from django.forms import ModelForm, Textarea
from repo.models import Dataset

class DatasetUploadForm(ModelForm):
    class Meta:
        model = Dataset
        fields = [ 'title', 'description', 'dataset' ]
        widgets = {
            'description': Textarea(attrs={ 'cols': 20, 'rows': 4}),
        }

class DatasetForm(ModelForm):
    class Meta:
        model = Dataset
        fields = [ 'title', 'description' ]
