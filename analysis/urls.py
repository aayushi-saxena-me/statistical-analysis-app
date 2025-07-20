from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # Main views
    path('', views.dashboard, name='dashboard'),
    path('update/', views.update_analysis, name='update_analysis'),
    path('about/', views.about, name='about'),
    
    # AJAX endpoints
    path('api/plots/', views.get_plots, name='get_plots'),
    path('api/statistics/', views.get_statistics, name='get_statistics'),
    path('api/data-preview/', views.get_data_preview, name='get_data_preview'),
    path('api/columns/', views.get_column_choices, name='get_column_choices'),
    path('api/upload/', views.upload_file, name='upload_file'),
    
    # SVM Machine Learning endpoints
    path('api/svm/train/', views.train_svm, name='train_svm'),
    path('api/svm/results/', views.get_svm_results, name='get_svm_results'),
    path('api/svm/status/', views.get_svm_status, name='get_svm_status'),
] 