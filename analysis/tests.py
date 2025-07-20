from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UploadedFile, AnalysisSession
from .utils import generate_random_data, get_summary_statistics
import pandas as pd
import json


class AnalysisViewTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_dashboard_view(self):
        """Test that dashboard loads successfully"""
        response = self.client.get(reverse('analysis:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Statistical Analysis Dashboard')
    
    def test_about_view(self):
        """Test that about page loads successfully"""
        response = self.client.get(reverse('analysis:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')
    
    def test_get_plots_endpoint(self):
        """Test the plots API endpoint"""
        response = self.client.get(reverse('analysis:get_plots'))
        self.assertEqual(response.status_code, 200)
        
        # Response should be JSON
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
    
    def test_get_statistics_endpoint(self):
        """Test the statistics API endpoint"""
        response = self.client.get(reverse('analysis:get_statistics'))
        self.assertEqual(response.status_code, 200)
        
        # Response should be JSON
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
    
    def test_get_data_preview_endpoint(self):
        """Test the data preview API endpoint"""
        response = self.client.get(reverse('analysis:get_data_preview'))
        self.assertEqual(response.status_code, 200)
        
        # Response should be JSON
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)


class ModelTests(TestCase):
    def test_uploaded_file_creation(self):
        """Test UploadedFile model creation"""
        # Create a simple CSV file
        csv_content = "col1,col2\n1,2\n3,4"
        uploaded_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        file_obj = UploadedFile.objects.create(
            file=uploaded_file,
            original_name="test.csv",
            file_size=len(csv_content)
        )
        
        self.assertEqual(file_obj.original_name, "test.csv")
        self.assertEqual(file_obj.file_size, len(csv_content))
        self.assertTrue(file_obj.uploaded_at)
    
    def test_analysis_session_creation(self):
        """Test AnalysisSession model creation"""
        session = AnalysisSession.objects.create(
            session_id="test-session-123",
            data_source="random",
            sample_size=100,
            color="blue",
            bins=30
        )
        
        self.assertEqual(session.session_id, "test-session-123")
        self.assertEqual(session.data_source, "random")
        self.assertEqual(session.sample_size, 100)
        self.assertTrue(session.created_at)
        self.assertTrue(session.updated_at)


class UtilityTests(TestCase):
    def test_generate_random_data(self):
        """Test random data generation"""
        data = generate_random_data(100)
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 100)
        self.assertIn('x', data.columns)
        self.assertIn('y', data.columns)
        self.assertIn('z', data.columns)
    
    def test_get_summary_statistics(self):
        """Test summary statistics calculation"""
        # Create test data
        data = pd.DataFrame({
            'test_col': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        })
        
        stats = get_summary_statistics(data, 'test_col')
        
        self.assertIsInstance(stats, dict)
        self.assertIn('mean', stats)
        self.assertIn('std', stats)
        self.assertIn('count', stats)
        self.assertEqual(stats['count'], 10)
        self.assertEqual(stats['mean'], 5.5)
    
    def test_get_summary_statistics_non_numeric(self):
        """Test summary statistics with non-numeric data"""
        data = pd.DataFrame({
            'text_col': ['a', 'b', 'c', 'd', 'e']
        })
        
        stats = get_summary_statistics(data, 'text_col')
        
        self.assertIsInstance(stats, dict)
        self.assertIn('error', stats)


class FormTests(TestCase):
    def test_analysis_form_validation(self):
        """Test form validation"""
        from .forms import AnalysisForm
        
        # Test valid form data
        form_data = {
            'data_source': 'random',
            'sample_size': 1000,
            'color': 'blue',
            'bins': 30,
            'show_plot': True,
            'show_stats': True,
            'show_correlation': True
        }
        
        form = AnalysisForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_analysis_form_upload_validation(self):
        """Test form validation for file upload"""
        from .forms import AnalysisForm
        
        # Test upload source without file - should be invalid
        form_data = {
            'data_source': 'upload',
            'color': 'blue',
            'bins': 30,
            'show_plot': True,
            'show_stats': True,
            'show_correlation': True
        }
        
        form = AnalysisForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please upload a file', str(form.errors)) 