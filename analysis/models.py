from django.db import models
from django.core.validators import FileExtensionValidator
import os


class UploadedFile(models.Model):
    """Model to store uploaded CSV files"""
    file = models.FileField(
        upload_to='uploads/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls'])]
    )
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.original_name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
    
    def delete(self, *args, **kwargs):
        # Delete the file from filesystem when model is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class AnalysisSession(models.Model):
    """Model to store analysis sessions and parameters"""
    session_id = models.CharField(max_length=100, unique=True)
    data_source = models.CharField(max_length=20, choices=[
        ('random', 'Random Data'),
        ('upload', 'Upload CSV'),
        ('local', 'Tumor Dataset')
    ])
    sample_size = models.IntegerField(null=True, blank=True)
    selected_column = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=20, default='blue')
    bins = models.IntegerField(default=30)
    show_plot = models.BooleanField(default=True)
    show_stats = models.BooleanField(default=True)
    show_correlation = models.BooleanField(default=True)
    # SVM configuration fields
    svm_target_column = models.CharField(max_length=100, null=True, blank=True)
    svm_kernel = models.CharField(max_length=20, default='rbf', choices=[
        ('linear', 'Linear'),
        ('poly', 'Polynomial'),
        ('rbf', 'RBF (Radial Basis Function)'),
        ('sigmoid', 'Sigmoid')
    ])
    svm_test_size = models.FloatField(default=0.2)
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Session {self.session_id} - {self.data_source}"


class SVMResults(models.Model):
    """Model to store SVM training results and metrics"""
    analysis_session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='svm_results')
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    kernel_type = models.CharField(max_length=20)
    test_size = models.FloatField()
    target_column = models.CharField(max_length=100)
    feature_columns = models.JSONField()  # Store list of feature column names
    class_labels = models.JSONField()  # Store class labels
    confusion_matrix = models.JSONField()  # Store confusion matrix as 2D array
    n_samples = models.IntegerField()
    n_features = models.IntegerField()
    n_train = models.IntegerField()
    n_test = models.IntegerField()
    training_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-training_date']
    
    def __str__(self):
        return f"SVM Results - {self.analysis_session.session_id} (Accuracy: {self.accuracy:.3f})" 