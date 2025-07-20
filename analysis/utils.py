import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.express as px
from scipy import stats
from scipy.stats import normaltest, shapiro
import io
import base64
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
import json


def generate_random_data(sample_size=1000):
    """Generate random data similar to R's rnorm"""
    np.random.seed(123)
    return pd.DataFrame({
        'x': np.random.normal(0, 1, sample_size),
        'y': np.random.normal(0, 1, sample_size),
        'z': np.random.normal(0, 1, sample_size)
    })


def load_csv_file(file_path):
    """Load CSV/Excel file with error handling"""
    try:
        # Determine file type by extension
        file_extension = file_path.lower().split('.')[-1]
        
        if file_extension in ['xlsx', 'xls']:
            # Load Excel file - read first sheet
            df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
            return df, None
        else:
            # Load CSV file with different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    return df, None
                except UnicodeDecodeError:
                    continue
            return None, "Unable to decode CSV file with common encodings"
    except Exception as e:
        return None, f"Error loading file: {str(e)}"


def get_summary_statistics(data, column=None):
    """Calculate summary statistics for a column or dataset"""
    if column and column in data.columns:
        series = data[column]
    elif len(data.columns) == 1:
        series = data.iloc[:, 0]
    else:
        # For multiple columns, return summary for all numeric columns
        return data.describe().to_dict()
    
    if not pd.api.types.is_numeric_dtype(series):
        return {"error": "Selected column is not numeric"}
    
    stats_dict = {
        'count': int(len(series)),
        'mean': float(series.mean()),
        'median': float(series.median()),
        'std': float(series.std()),
        'var': float(series.var()),
        'min': float(series.min()),
        'max': float(series.max()),
        'q25': float(series.quantile(0.25)),
        'q75': float(series.quantile(0.75)),
        'skewness': float(stats.skew(series)),
        'kurtosis': float(stats.kurtosis(series))
    }
    return stats_dict


def perform_hypothesis_test(data, column=None, test_value=0):
    """Perform one-sample t-test"""
    if column and column in data.columns:
        series = data[column]
    elif len(data.columns) == 1:
        series = data.iloc[:, 0]
    else:
        series = data.iloc[:, 0]  # Default to first column
    
    if not pd.api.types.is_numeric_dtype(series):
        return {"error": "Selected column is not numeric"}
    
    # One-sample t-test
    t_stat, p_value = stats.ttest_1samp(series, test_value)
    
    # Normality tests
    shapiro_result = shapiro(series[:5000] if len(series) > 5000 else series)  # Shapiro limited to 5000 samples
    shapiro_stat, shapiro_p = shapiro_result
    
    try:
        return {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'test_value': float(test_value),
            'sample_mean': float(series.mean()),
            'shapiro_statistic': float(shapiro_stat),
            'shapiro_p_value': float(shapiro_p),
            'is_normal': bool(shapiro_p > 0.05)
        }
    except (TypeError, ValueError):
        # Fallback for any conversion issues
        return {
            't_statistic': str(t_stat),
            'p_value': str(p_value),
            'test_value': float(test_value),
            'sample_mean': float(series.mean()),
            'shapiro_statistic': str(shapiro_stat),
            'shapiro_p_value': str(shapiro_p),
            'is_normal': bool(shapiro_p > 0.05)
        }


def create_histogram_plotly(data, column, bins=30, color='blue'):
    """Create histogram using Plotly"""
    if column not in data.columns:
        return None
    
    series = data[column]
    if not pd.api.types.is_numeric_dtype(series):
        return None
    
    fig = px.histogram(
        data, 
        x=column, 
        nbins=bins,
        title=f'Distribution of {column}',
        color_discrete_sequence=[color.lower()]
    )
    
    fig.update_layout(
        xaxis_title="Value",
        yaxis_title="Count",
        template="plotly_white"
    )
    
    return fig.to_json()


def create_boxplot_plotly(data, column=None):
    """Create box plot using Plotly"""
    if column and column in data.columns:
        if not pd.api.types.is_numeric_dtype(data[column]):
            return None
        
        fig = go.Figure()
        fig.add_trace(go.Box(y=data[column], name=column))
        fig.update_layout(
            title=f'Box Plot of {column}',
            yaxis_title="Value",
            template="plotly_white"
        )
    else:
        # Multiple columns - show all numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return None
        
        fig = go.Figure()
        for col in numeric_cols:
            fig.add_trace(go.Box(y=data[col], name=col))
        
        fig.update_layout(
            title='Box Plot',
            yaxis_title="Value",
            template="plotly_white"
        )
    
    return fig.to_json()


def create_qq_plot_plotly(data, column):
    """Create Q-Q plot using Plotly"""
    if column not in data.columns:
        return None
    
    series = data[column].dropna()
    if not pd.api.types.is_numeric_dtype(series):
        return None
    
    # Generate theoretical quantiles
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(series)))
    sample_quantiles = np.sort(series)
    
    fig = go.Figure()
    
    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=theoretical_quantiles,
        y=sample_quantiles,
        mode='markers',
        name='Sample Quantiles',
        marker=dict(color='blue', size=4)
    ))
    
    # Add reference line
    min_val = min(theoretical_quantiles.min(), sample_quantiles.min())
    max_val = max(theoretical_quantiles.max(), sample_quantiles.max())
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Reference Line',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f'Q-Q Plot of {column}',
        xaxis_title="Theoretical Quantiles",
        yaxis_title="Sample Quantiles",
        template="plotly_white"
    )
    
    return fig.to_json()


def create_correlation_plot_plotly(data):
    """Create correlation heatmap using Plotly"""
    numeric_data = data.select_dtypes(include=[np.number])
    if len(numeric_data.columns) < 2:
        return None
    
    corr_matrix = numeric_data.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title='Correlation Matrix',
        template="plotly_white",
        width=600,
        height=600
    )
    
    return fig.to_json()


def get_data_info(data):
    """Get basic information about the dataset"""
    info = {
        'shape': data.shape,
        'columns': list(data.columns),
        'dtypes': dict(data.dtypes.astype(str)),
        'missing_values': dict(data.isnull().sum()),
        'numeric_columns': list(data.select_dtypes(include=[np.number]).columns),
        'categorical_columns': list(data.select_dtypes(include=['object']).columns)
    }
    return info


# SVM Machine Learning Functions

def prepare_svm_data(data, target_column=None):
    """Prepare data for SVM training - use all columns except last as features, last as target if not specified"""
    try:
        # Remove rows with any missing values
        data_clean = data.dropna()
        
        if data_clean.empty:
            return None, None, None, None, "No data remaining after removing missing values"
        
        # Determine target column
        if target_column is None:
            target_column = data_clean.columns[-1]  # Use last column as target
        
        if target_column not in data_clean.columns:
            return None, None, None, None, f"Target column '{target_column}' not found in data"
        
        # Separate features and target
        feature_columns = [col for col in data_clean.columns if col != target_column]
        
        if len(feature_columns) == 0:
            return None, None, None, None, "No feature columns available for training"
        
        X = data_clean[feature_columns]
        y = data_clean[target_column]
        
        # Handle non-numeric features
        for col in X.columns:
            if not pd.api.types.is_numeric_dtype(X[col]):
                # Convert categorical to numeric using label encoding
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
        
        # Handle non-numeric target
        label_encoder = None
        if not pd.api.types.is_numeric_dtype(y):
            label_encoder = LabelEncoder()
            y = label_encoder.fit_transform(y.astype(str))
        
        return X, y, feature_columns, label_encoder, None
        
    except Exception as e:
        return None, None, None, None, f"Error preparing data: {str(e)}"


def train_svm_model(data, target_column=None, test_size=0.2, kernel='rbf', random_state=42):
    """Train SVM model and return results"""
    try:
        # Prepare data
        X, y, feature_columns, label_encoder, error = prepare_svm_data(data, target_column)
        if error:
            return None, error
        
        if len(X) < 10:
            return None, "Insufficient data for training (minimum 10 samples required)"
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train SVM model
        svm_model = SVC(kernel=kernel, random_state=random_state)
        svm_model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = svm_model.predict(X_test_scaled)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Handle binary vs multiclass metrics
        average_method = 'binary' if len(np.unique(y)) == 2 else 'weighted'
        precision = precision_score(y_test, y_pred, average=average_method, zero_division=0)
        recall = recall_score(y_test, y_pred, average=average_method, zero_division=0)
        f1 = f1_score(y_test, y_pred, average=average_method, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Get class labels
        if label_encoder:
            class_labels = label_encoder.classes_
        else:
            class_labels = np.unique(y)
        
        results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm.tolist(),
            'class_labels': class_labels.tolist(),
            'feature_columns': feature_columns,
            'target_column': target_column or data.columns[-1],
            'kernel': kernel,
            'test_size': test_size,
            'n_samples': len(data),
            'n_features': len(feature_columns),
            'n_train': len(X_train),
            'n_test': len(X_test)
        }
        
        return results, None
        
    except Exception as e:
        return None, f"Error training SVM model: {str(e)}"


def create_confusion_matrix_plotly(confusion_matrix, class_labels):
    """Create confusion matrix heatmap using Plotly"""
    try:
        fig = go.Figure(data=go.Heatmap(
            z=confusion_matrix,
            x=[f"Predicted {label}" for label in class_labels],
            y=[f"Actual {label}" for label in class_labels],
            colorscale='Blues',
            text=confusion_matrix,
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Confusion Matrix',
            xaxis_title="Predicted",
            yaxis_title="Actual",
            template="plotly_white",
            width=500,
            height=500
        )
        
        return fig.to_json()
        
    except Exception as e:
        return None


def create_svm_metrics_plot(results):
    """Create bar chart of SVM performance metrics"""
    try:
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        values = [results['accuracy'], results['precision'], results['recall'], results['f1_score']]
        
        fig = go.Figure(data=go.Bar(
            x=metrics,
            y=values,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
            text=[f"{v:.3f}" for v in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='SVM Model Performance Metrics',
            xaxis_title="Metrics",
            yaxis_title="Score",
            yaxis=dict(range=[0, 1]),
            template="plotly_white",
            showlegend=False
        )
        
        return fig.to_json()
        
    except Exception as e:
        return None


def get_svm_feature_columns(data, target_column=None):
    """Get list of feature columns for SVM (all except target)"""
    if target_column is None:
        target_column = data.columns[-1]
    
    feature_columns = [col for col in data.columns if col != target_column]
    return feature_columns


def validate_svm_data(data):
    """Validate that data is suitable for SVM training"""
    if data is None or data.empty:
        return False, "No data available"
    
    if len(data.columns) < 2:
        return False, "At least 2 columns required (features + target)"
    
    if len(data) < 10:
        return False, "At least 10 samples required for training"
    
    # Check if we have at least one feature column after removing target
    feature_columns = data.columns[:-1]  # All except last
    if len(feature_columns) == 0:
        return False, "No feature columns available"
    
    return True, "Data is suitable for SVM training" 