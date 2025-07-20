from django.contrib import admin
from .models import UploadedFile, AnalysisSession


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['original_name']
    readonly_fields = ['uploaded_at']
    ordering = ['-uploaded_at']
    
    def get_readonly_fields(self, request, obj=None):
        # Make file_size readonly as well
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # If editing existing object
            readonly_fields.extend(['file', 'file_size', 'original_name'])
        return readonly_fields


@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'data_source', 'selected_column', 'created_at', 'updated_at']
    list_filter = ['data_source', 'created_at', 'updated_at']
    search_fields = ['session_id', 'selected_column']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'created_at', 'updated_at')
        }),
        ('Data Configuration', {
            'fields': ('data_source', 'sample_size', 'selected_column', 'uploaded_file')
        }),
        ('Visualization Settings', {
            'fields': ('color', 'bins')
        }),
        ('Display Options', {
            'fields': ('show_plot', 'show_stats', 'show_correlation')
        }),
    )
    
    def get_queryset(self, request):
        # Optimize queries by selecting related objects
        return super().get_queryset(request).select_related('uploaded_file') 