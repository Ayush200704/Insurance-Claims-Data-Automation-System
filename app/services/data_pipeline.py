"""
Data Pipeline Service for Insurance Claims Processing
Handles extraction, cleaning, and transformation of insurance claims data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re
from loguru import logger
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

from app.core.database import get_claims_data, load_data_to_db


class DataPipelineService:
    """Service for processing insurance claims data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model = None
        self.feature_columns = ['age', 'bmi', 'children', 'smoker', 'region_encoded', 'sex_encoded']
        
    def extract_data(self, file_path: str) -> pd.DataFrame:
        """
        Extract data from CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DataFrame with extracted data
        """
        try:
            logger.info(f"Extracting data from {file_path}")
            df = pd.read_csv(file_path)
            logger.info(f"Successfully extracted {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            raise
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate insurance claims data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            logger.info("Starting data cleaning process")
            df_clean = df.copy()
            
            # Standardize column names
            df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
            
            # Handle missing values
            df_clean = self._handle_missing_values(df_clean)
            
            # Validate data types and ranges
            df_clean = self._validate_data_types(df_clean)
            
            # Remove outliers
            df_clean = self._remove_outliers(df_clean)
            
            # Standardize categorical variables
            df_clean = self._standardize_categoricals(df_clean)
            
            logger.info(f"Data cleaning completed. {len(df_clean)} records remaining")
            return df_clean
            
        except Exception as e:
            logger.error(f"Error in data cleaning: {e}")
            raise
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data for analysis and modeling
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Transformed DataFrame
        """
        try:
            logger.info("Starting data transformation")
            df_transformed = df.copy()
            
            # Encode categorical variables
            df_transformed = self._encode_categoricals(df_transformed)
            
            # Create derived features
            df_transformed = self._create_derived_features(df_transformed)
            
            # Scale numerical features
            df_transformed = self._scale_features(df_transformed)
            
            logger.info("Data transformation completed")
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error in data transformation: {e}")
            raise
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        logger.info("Handling missing values")
        
        # Check for missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            logger.warning(f"Found missing values: {missing_counts[missing_counts > 0].to_dict()}")
            
            # Fill missing values based on data type
            for column in df.columns:
                if df[column].dtype in ['int64', 'float64']:
                    df[column].fillna(df[column].median(), inplace=True)
                else:
                    df[column].fillna(df[column].mode()[0] if not df[column].mode().empty else 'Unknown', inplace=True)
        
        return df
    
    def _validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and convert data types"""
        logger.info("Validating data types")
        
        # Convert age to integer
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce').astype('Int64')
        
        # Convert bmi to float
        if 'bmi' in df.columns:
            df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')
        
        # Convert children to integer
        if 'children' in df.columns:
            df['children'] = pd.to_numeric(df['children'], errors='coerce').astype('Int64')
        
        # Convert charges to float
        if 'charges' in df.columns:
            df['charges'] = pd.to_numeric(df['charges'], errors='coerce')
        
        # Convert smoker to integer (0/1 format)
        if 'smoker' in df.columns:
            df['smoker'] = pd.to_numeric(df['smoker'], errors='coerce').astype('Int64')
        
        # Convert sex to integer (0/1 format)
        if 'sex' in df.columns:
            df['sex'] = pd.to_numeric(df['sex'], errors='coerce').astype('Int64')
        
        # Convert region to integer (0-3 format)
        if 'region' in df.columns:
            df['region'] = pd.to_numeric(df['region'], errors='coerce').astype('Int64')
        
        # Keep insurance claim column as is (already in correct format)
        if 'insuranceclaim' in df.columns:
            df['insuranceclaim'] = pd.to_numeric(df['insuranceclaim'], errors='coerce').astype('Int64')
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers using IQR method"""
        logger.info("Removing outliers")
        
        numerical_columns = ['age', 'bmi', 'charges']
        
        for column in numerical_columns:
            if column in df.columns:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_count = len(df[(df[column] < lower_bound) | (df[column] > upper_bound)])
                if outliers_count > 0:
                    logger.info(f"Removing {outliers_count} outliers from {column}")
                    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        
        return df
    
    def _standardize_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize categorical variables"""
        logger.info("Standardizing categorical variables")
        
        # Data is already in numeric format (0/1 for sex, 0-3 for region)
        # No additional standardization needed for this dataset
        
        return df
    
    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        logger.info("Encoding categorical variables")
        
        # Data is already encoded (0/1 for sex, 0-3 for region)
        # Create encoded columns for consistency with model features
        if 'sex' in df.columns:
            df['sex_encoded'] = df['sex']
        
        if 'region' in df.columns:
            df['region_encoded'] = df['region']
        
        return df
    
    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features for better modeling"""
        logger.info("Creating derived features")
        
        # BMI categories
        if 'bmi' in df.columns:
            df['bmi_category'] = pd.cut(df['bmi'], 
                                      bins=[0, 18.5, 25, 30, float('inf')], 
                                      labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
        
        # Age groups
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'], 
                                   bins=[0, 30, 45, 60, float('inf')], 
                                   labels=['Young', 'Middle', 'Senior', 'Elderly'])
        
        # Risk score (combination of age, bmi, smoker status)
        if all(col in df.columns for col in ['age', 'bmi', 'smoker']):
            df['risk_score'] = (
                (df['age'] / 100) * 0.4 +
                (df['bmi'] / 50) * 0.3 +
                df['smoker'] * 0.3
            )
        
        return df
    
    def _scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        logger.info("Scaling numerical features")
        
        numerical_columns = ['age', 'bmi', 'children', 'risk_score']
        existing_columns = [col for col in numerical_columns if col in df.columns]
        
        if existing_columns:
            df[existing_columns] = self.scaler.fit_transform(df[existing_columns])
        
        return df
    
    def train_model(self, df: pd.DataFrame) -> Dict:
        """
        Train machine learning model for claims prediction
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            Model performance metrics
        """
        try:
            logger.info("Training machine learning model")
            
            # Prepare features and target
            X = df[self.feature_columns]
            y = df['insuranceclaim']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = self.model.score(X_test, y_test)
            
            # Generate classification report
            report = classification_report(y_test, y_pred, output_dict=True)
            
            # Save model
            model_path = "models/claims_model.pkl"
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(self.model, model_path)
            
            logger.info(f"Model trained successfully. Accuracy: {accuracy:.4f}")
            
            return {
                'accuracy': float(accuracy),
                'classification_report': self._convert_numpy_types(report),
                'model_path': model_path
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict_claims(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict insurance claims for new data
        
        Args:
            df: DataFrame with features
            
        Returns:
            DataFrame with predictions
        """
        try:
            if self.model is None:
                # Load saved model
                model_path = "models/claims_model.pkl"
                if os.path.exists(model_path):
                    self.model = joblib.load(model_path)
                else:
                    raise ValueError("Model not found. Please train the model first.")
            
            # Prepare features
            X = df[self.feature_columns]
            
            # Make predictions
            predictions = self.model.predict(X)
            probabilities = self.model.predict_proba(X)[:, 1]
            
            # Add predictions to DataFrame
            df_result = df.copy()
            df_result['predicted_claim'] = predictions
            df_result['claim_probability'] = probabilities
            
            return df_result
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            raise
    
    def process_pipeline(self, file_path: str) -> Dict:
        """
        Complete data pipeline processing
        
        Args:
            file_path: Path to input CSV file
            
        Returns:
            Processing results and statistics
        """
        try:
            logger.info("Starting complete data pipeline processing")
            
            # Extract data
            df_raw = self.extract_data(file_path)
            
            # Clean data
            df_clean = self.clean_data(df_raw)
            
            # Transform data
            df_transformed = self.transform_data(df_clean)
            
            # Load to database
            records_loaded = load_data_to_db(file_path)
            
            # Train model
            model_results = self.train_model(df_transformed)
            
            # Generate summary statistics
            summary_stats = self._generate_summary_stats(df_transformed)
            
            logger.info("Data pipeline processing completed successfully")
            
            return {
                'records_processed': int(len(df_transformed)),
                'records_loaded': int(records_loaded),
                'summary_statistics': self._convert_numpy_types(summary_stats),
                'model_performance': self._convert_numpy_types(model_results)
            }
            
        except Exception as e:
            logger.error(f"Error in pipeline processing: {e}")
            raise
    
    def _generate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the dataset"""
        stats = {
            'total_records': int(len(df)),
            'claim_rate': float(df['insuranceclaim'].mean()) if 'insuranceclaim' in df.columns else 0.0,
            'average_age': float(df['age'].mean()) if 'age' in df.columns else 0.0,
            'average_bmi': float(df['bmi'].mean()) if 'bmi' in df.columns else 0.0,
            'average_charges': float(df['charges'].mean()) if 'charges' in df.columns else 0.0,
            'smoker_rate': float(df['smoker'].mean()) if 'smoker' in df.columns else 0.0,
            'sex_distribution': {int(k): int(v) for k, v in df['sex'].value_counts().to_dict().items()} if 'sex' in df.columns else {},
            'region_distribution': {int(k): int(v) for k, v in df['region'].value_counts().to_dict().items()} if 'region' in df.columns else {}
        }
        
        return stats
    
    def _convert_numpy_types(self, obj):
        """Convert NumPy types to Python native types for JSON serialization"""
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
