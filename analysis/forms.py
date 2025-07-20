from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import UploadedFile


class AnalysisForm(forms.Form):
    DATA_SOURCE_CHOICES = [
        ('random', 'Random Data'),
        ('upload', 'Upload CSV'),
        ('local', 'Tumor Dataset'),
    ]
    
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('purple', 'Purple'),
    ]
    
    SVM_KERNEL_CHOICES = [
        ('linear', 'Linear'),
        ('poly', 'Polynomial'),
        ('rbf', 'RBF (Radial Basis Function)'),
        ('sigmoid', 'Sigmoid'),
    ]
    
    TEST_SIZE_CHOICES = [
        (0.1, '10% Test / 90% Train'),
        (0.2, '20% Test / 80% Train'),
        (0.3, '30% Test / 70% Train'),
        (0.4, '40% Test / 60% Train'),
    ]
    
    data_source = forms.ChoiceField(
        choices=DATA_SOURCE_CHOICES,
        initial='local',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    # File upload field
    uploaded_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': '.csv,.xlsx,.xls',
            'class': 'form-control'
        }),
        help_text='Upload a CSV, Excel (.xlsx), or Excel (.xls) file'
    )
    
    # Sample size for random data
    sample_size = forms.IntegerField(
        initial=1000,
        min_value=100,
        max_value=10000,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Column selection (will be populated dynamically)
    selected_column = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Visualization options
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        initial='blue',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    bins = forms.IntegerField(
        initial=30,
        min_value=1,
        max_value=50,
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'class': 'form-range',
            'oninput': 'this.nextElementSibling.value = this.value'
        })
    )
    
    # Display options
    show_plot = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_stats = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_correlation = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # SVM Configuration Fields
    svm_target_column = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select target column for SVM (default: last column)'
    )
    
    svm_kernel = forms.ChoiceField(
        choices=SVM_KERNEL_CHOICES,
        initial='rbf',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='SVM kernel type'
    )
    
    svm_test_size = forms.ChoiceField(
        choices=TEST_SIZE_CHOICES,
        initial=0.2,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Train/test split ratio'
    )
    
    enable_svm = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Enable SVM machine learning analysis'
    )
    
    def __init__(self, *args, **kwargs):
        column_choices = kwargs.pop('column_choices', [])
        svm_target_choices = kwargs.pop('svm_target_choices', [])
        super().__init__(*args, **kwargs)
        
        if column_choices:
            self.fields['selected_column'].choices = column_choices
        
        if svm_target_choices:
            self.fields['svm_target_column'].choices = svm_target_choices
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.layout = Layout(
            HTML('<div class="card">'),
            HTML('<div class="card-header"><h5>Analysis Configuration</h5></div>'),
            HTML('<div class="card-body">'),
            
            # Data Source Section
            HTML('<h6 class="text-primary">Data Source</h6>'),
            'data_source',
            
            # Conditional fields based on data source
            HTML('<div id="upload-section" style="display:none;">'),
            'uploaded_file',
            HTML('</div>'),
            
            HTML('<div id="random-section" style="display:none;">'),
            Row(Column('sample_size', css_class='col-md-6')),
            HTML('</div>'),
            
            HTML('<div id="column-section" style="display:none;">'),
            Row(Column('selected_column', css_class='col-md-6')),
            HTML('</div>'),
            
            HTML('<hr>'),
            
            # Visualization Options
            HTML('<h6 class="text-primary">Visualization Options</h6>'),
            Row(
                Column('color', css_class='col-md-4'),
                Column('bins', css_class='col-md-4'),
            ),
            
            HTML('<div class="d-flex align-items-center mb-3">'),
            HTML('<span class="me-2">Bins:</span>'),
            HTML('<output class="form-control-plaintext">30</output>'),
            HTML('</div>'),
            
            HTML('<hr>'),
            
            # Display Options
            HTML('<h6 class="text-primary">Display Options</h6>'),
            Row(
                Column('show_plot', css_class='col-md-4'),
                Column('show_stats', css_class='col-md-4'),
                Column('show_correlation', css_class='col-md-4'),
            ),
            
            HTML('<hr>'),
            
            # SVM Machine Learning Options
            HTML('<h6 class="text-primary">Machine Learning (SVM)</h6>'),
            'enable_svm',
            HTML('<div id="svm-config-section" style="display:none;">'),
            Row(
                Column('svm_target_column', css_class='col-md-6'),
                Column('svm_kernel', css_class='col-md-6'),
            ),
            Row(
                Column('svm_test_size', css_class='col-md-6'),
            ),
            HTML('</div>'),
            
            HTML('</div>'),
            HTML('</div>'),
            
            HTML('<div class="mt-3">'),
            Submit('submit', 'Update Analysis', css_class='btn btn-primary btn-lg'),
            HTML('</div>'),
        )
    
    def clean(self):
        cleaned_data = super().clean()
        data_source = cleaned_data.get('data_source')
        selected_column = cleaned_data.get('selected_column')
        enable_svm = cleaned_data.get('enable_svm')
        
        if data_source == 'upload' and not cleaned_data.get('uploaded_file'):
            raise forms.ValidationError('Please upload a file when using "Upload CSV" option.')
        
        # Handle column validation for different data sources
        if data_source == 'random':
            # For random data, ensure we have a valid column
            if not selected_column or selected_column not in ['x', 'y', 'z']:
                cleaned_data['selected_column'] = 'x'
            # Disable SVM for random data (not suitable for classification)
            if enable_svm:
                self.add_error('enable_svm', 'SVM is not available for random data. Please upload a dataset.')
                cleaned_data['enable_svm'] = False
        elif data_source in ['local', 'upload']:
            # For local/upload data, if selected column is invalid, clear it
            # The view will set a default valid column
            if selected_column in ['x', 'y', 'z']:  # These are only valid for random data
                cleaned_data['selected_column'] = None
        
        # Clear SVM fields if SVM is not enabled to avoid validation errors
        if not enable_svm:
            cleaned_data['svm_target_column'] = ''
            cleaned_data['svm_kernel'] = 'rbf'
            cleaned_data['svm_test_size'] = 0.2
        
        return cleaned_data

    def clean_selected_column(self):
        selected_column = self.cleaned_data.get('selected_column')
        data_source = self.cleaned_data.get('data_source')
        
        # If no column is selected, that's OK for some cases
        if not selected_column:
            return selected_column
        
        # For random data, ensure the column is valid
        if data_source == 'random' and selected_column not in ['x', 'y', 'z']:
            # Don't raise error, just return a default
            return 'x'
        
        return selected_column
    
    def clean_svm_target_column(self):
        svm_target_column = self.cleaned_data.get('svm_target_column')
        enable_svm = self.cleaned_data.get('enable_svm')
        
        # If SVM is not enabled, return empty string to avoid validation errors
        if not enable_svm:
            return ''
        
        # If SVM is enabled but no target column selected, that's OK - return as is
        return svm_target_column


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.csv,.xlsx,.xls',
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {'enctype': 'multipart/form-data'}
        self.helper.layout = Layout(
            'file',
            Submit('upload', 'Upload File', css_class='btn btn-success')
        ) 