"""
Machine Learning service - provides ML capabilities for data analysis.
"""

import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

from app.core.logging import LoggerMixin


class MLModel:
    """ML Model wrapper."""
    
    def __init__(
        self,
        model_name: str,
        model_type: str,
        model: Any,
        scaler: Optional[StandardScaler] = None,
        encoders: Optional[Dict[str, LabelEncoder]] = None,
        feature_columns: Optional[List[str]] = None,
        target_column: Optional[str] = None,
        created_at: datetime = None
    ):
        self.model_name = model_name
        self.model_type = model_type
        self.model = model
        self.scaler = scaler
        self.encoders = encoders or {}
        self.feature_columns = feature_columns or []
        self.target_column = target_column
        self.created_at = created_at or datetime.utcnow()
        self.accuracy: Optional[float] = None
        self.metrics: Dict[str, Any] = {}


class MLPrediction:
    """ML Prediction result."""
    
    def __init__(
        self,
        prediction: Any,
        probability: Optional[float] = None,
        confidence: Optional[float] = None,
        model_info: Optional[Dict[str, Any]] = None
    ):
        self.prediction = prediction
        self.probability = probability
        self.confidence = confidence
        self.model_info = model_info or {}


class MLService(LoggerMixin):
    """Service for machine learning operations."""
    
    def __init__(self):
        self.models: Dict[str, MLModel] = {}
        self.model_storage_path = "/app/models"
    
    async def prepare_data_for_ml(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None,
        feature_selection: bool = True
    ) -> Tuple[pd.DataFrame, List[str], Optional[str]]:
        """Prepare data for machine learning."""
        self.logger.info(f"Preparing data for ML: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Create a copy to avoid modifying original
        ml_df = df.copy()
        
        # Handle missing values
        ml_df = self._handle_missing_values(ml_df)
        
        # Encode categorical variables
        ml_df, encoders = self._encode_categorical_variables(ml_df)
        
        # Select features
        if feature_selection:
            feature_columns = self._select_features(ml_df, target_column)
        else:
            feature_columns = [col for col in ml_df.columns if col != target_column]
        
        self.logger.info(f"Selected {len(feature_columns)} features for ML")
        
        return ml_df, feature_columns, target_column
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        # For numeric columns, use median imputation
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            numeric_imputer = SimpleImputer(strategy='median')
            df[numeric_columns] = numeric_imputer.fit_transform(df[numeric_columns])
        
        # For categorical columns, use mode imputation
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            categorical_imputer = SimpleImputer(strategy='most_frequent')
            df[categorical_columns] = categorical_imputer.fit_transform(df[categorical_columns])
        
        return df
    
    def _encode_categorical_variables(
        self, 
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
        """Encode categorical variables."""
        encoders = {}
        
        for column in df.select_dtypes(include=['object']).columns:
            if df[column].nunique() < 50:  # Only encode if not too many unique values
                encoder = LabelEncoder()
                df[column] = encoder.fit_transform(df[column].astype(str))
                encoders[column] = encoder
        
        return df, encoders
    
    def _select_features(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None
    ) -> List[str]:
        """Select relevant features for ML."""
        # Remove target column if specified
        feature_df = df.copy()
        if target_column and target_column in feature_df.columns:
            feature_df = feature_df.drop(columns=[target_column])
        
        # Remove columns with too many missing values
        feature_df = feature_df.dropna(axis=1, thresh=len(feature_df) * 0.5)
        
        # Remove columns with constant values
        feature_df = feature_df.loc[:, (feature_df != feature_df.iloc[0]).any()]
        
        # Remove highly correlated features
        numeric_columns = feature_df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 1:
            corr_matrix = feature_df[numeric_columns].corr().abs()
            upper_tri = corr_matrix.where(
                np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
            )
            
            to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > 0.95)]
            feature_df = feature_df.drop(columns=to_drop)
        
        return feature_df.columns.tolist()
    
    async def train_classification_model(
        self,
        df: pd.DataFrame,
        target_column: str,
        model_name: str = "classification_model",
        test_size: float = 0.2,
        random_state: int = 42
    ) -> MLModel:
        """Train a classification model."""
        self.logger.info(f"Training classification model for target: {target_column}")
        
        # Prepare data
        ml_df, feature_columns, _ = await self.prepare_data_for_ml(
            df, target_column, feature_selection=True
        )
        
        # Check if target is categorical
        if not ml_df[target_column].dtype in ['object', 'category']:
            # Convert numeric target to categorical if it has few unique values
            if ml_df[target_column].nunique() <= 10:
                ml_df[target_column] = ml_df[target_column].astype(str)
            else:
                raise ValueError("Target column should be categorical or have few unique values")
        
        # Prepare features and target
        X = ml_df[feature_columns]
        y = ml_df[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        accuracy = model.score(X_test_scaled, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        # Create MLModel object
        ml_model = MLModel(
            model_name=model_name,
            model_type="classification",
            model=model,
            scaler=scaler,
            feature_columns=feature_columns,
            target_column=target_column
        )
        
        ml_model.accuracy = accuracy
        ml_model.metrics = {
            "accuracy": accuracy,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True)
        }
        
        # Store model
        self.models[model_name] = ml_model
        
        self.logger.info(f"Classification model trained with accuracy: {accuracy:.3f}")
        
        return ml_model
    
    async def train_regression_model(
        self,
        df: pd.DataFrame,
        target_column: str,
        model_name: str = "regression_model",
        test_size: float = 0.2,
        random_state: int = 42
    ) -> MLModel:
        """Train a regression model."""
        self.logger.info(f"Training regression model for target: {target_column}")
        
        # Prepare data
        ml_df, feature_columns, _ = await self.prepare_data_for_ml(
            df, target_column, feature_selection=True
        )
        
        # Ensure target is numeric
        if not pd.api.types.is_numeric_dtype(ml_df[target_column]):
            try:
                ml_df[target_column] = pd.to_numeric(ml_df[target_column])
            except:
                raise ValueError("Target column must be numeric for regression")
        
        # Prepare features and target
        X = ml_df[feature_columns]
        y = ml_df[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            random_state=random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        
        # Create MLModel object
        ml_model = MLModel(
            model_name=model_name,
            model_type="regression",
            model=model,
            scaler=scaler,
            feature_columns=feature_columns,
            target_column=target_column
        )
        
        ml_model.accuracy = r2  # Use R² as accuracy metric for regression
        ml_model.metrics = {
            "mse": mse,
            "rmse": np.sqrt(mse),
            "r2_score": r2,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std()
        }
        
        # Store model
        self.models[model_name] = ml_model
        
        self.logger.info(f"Regression model trained with R²: {r2:.3f}")
        
        return ml_model
    
    async def train_clustering_model(
        self,
        df: pd.DataFrame,
        n_clusters: int = 3,
        model_name: str = "clustering_model",
        random_state: int = 42
    ) -> MLModel:
        """Train a clustering model."""
        self.logger.info(f"Training clustering model with {n_clusters} clusters")
        
        # Prepare data (no target column for clustering)
        ml_df, feature_columns, _ = await self.prepare_data_for_ml(
            df, target_column=None, feature_selection=True
        )
        
        # Prepare features
        X = ml_df[feature_columns]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        model = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10
        )
        
        model.fit(X_scaled)
        
        # Evaluate model (inertia)
        inertia = model.inertia_
        
        # Create MLModel object
        ml_model = MLModel(
            model_name=model_name,
            model_type="clustering",
            model=model,
            scaler=scaler,
            feature_columns=feature_columns
        )
        
        ml_model.metrics = {
            "inertia": inertia,
            "n_clusters": n_clusters,
            "silhouette_score": self._calculate_silhouette_score(X_scaled, model.labels_)
        }
        
        # Store model
        self.models[model_name] = ml_model
        
        self.logger.info(f"Clustering model trained with inertia: {inertia:.3f}")
        
        return ml_model
    
    def _calculate_silhouette_score(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering."""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(X, labels)
        except:
            return 0.0
    
    async def predict(
        self,
        model_name: str,
        data: pd.DataFrame
    ) -> MLPrediction:
        """Make predictions using a trained model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        ml_model = self.models[model_name]
        
        # Prepare data
        prediction_df = data.copy()
        
        # Handle missing values
        prediction_df = self._handle_missing_values(prediction_df)
        
        # Encode categorical variables using stored encoders
        for column, encoder in ml_model.encoders.items():
            if column in prediction_df.columns:
                prediction_df[column] = encoder.transform(prediction_df[column].astype(str))
        
        # Select features
        available_features = [col for col in ml_model.feature_columns if col in prediction_df.columns]
        if len(available_features) != len(ml_model.feature_columns):
            missing_features = set(ml_model.feature_columns) - set(available_features)
            self.logger.warning(f"Missing features: {missing_features}")
        
        X = prediction_df[available_features]
        
        # Scale features
        X_scaled = ml_model.scaler.transform(X)
        
        # Make prediction
        prediction = ml_model.model.predict(X_scaled)
        
        # Calculate confidence/probability
        confidence = None
        probability = None
        
        if ml_model.model_type == "classification":
            if hasattr(ml_model.model, 'predict_proba'):
                probabilities = ml_model.model.predict_proba(X_scaled)
                probability = float(np.max(probabilities))
                confidence = probability
        elif ml_model.model_type == "regression":
            # For regression, we could calculate prediction intervals
            confidence = 0.8  # Placeholder
        
        return MLPrediction(
            prediction=prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            probability=probability,
            confidence=confidence,
            model_info={
                "model_name": model_name,
                "model_type": ml_model.model_type,
                "accuracy": ml_model.accuracy
            }
        )
    
    async def get_feature_importance(
        self,
        model_name: str,
        top_n: int = 10
    ) -> Dict[str, float]:
        """Get feature importance from a trained model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        ml_model = self.models[model_name]
        
        if not hasattr(ml_model.model, 'feature_importances_'):
            raise ValueError(f"Model {model_name} does not support feature importance")
        
        importances = ml_model.model.feature_importances_
        feature_names = ml_model.feature_columns
        
        # Create feature importance dictionary
        importance_dict = dict(zip(feature_names, importances))
        
        # Sort by importance and return top N
        sorted_features = sorted(
            importance_dict.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        return dict(sorted_features)
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a trained model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        ml_model = self.models[model_name]
        
        return {
            "model_name": ml_model.model_name,
            "model_type": ml_model.model_type,
            "feature_columns": ml_model.feature_columns,
            "target_column": ml_model.target_column,
            "accuracy": ml_model.accuracy,
            "metrics": ml_model.metrics,
            "created_at": ml_model.created_at.isoformat()
        }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all trained models."""
        return [
            {
                "model_name": name,
                "model_type": model.model_type,
                "accuracy": model.accuracy,
                "created_at": model.created_at.isoformat()
            }
            for name, model in self.models.items()
        ]
    
    async def save_model(self, model_name: str, file_path: Optional[str] = None) -> str:
        """Save a trained model to disk."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        ml_model = self.models[model_name]
        
        if not file_path:
            file_path = f"{self.model_storage_path}/{model_name}.joblib"
        
        # Save model
        joblib.dump(ml_model, file_path)
        
        self.logger.info(f"Model {model_name} saved to {file_path}")
        
        return file_path
    
    async def load_model(self, file_path: str) -> MLModel:
        """Load a model from disk."""
        ml_model = joblib.load(file_path)
        
        if not isinstance(ml_model, MLModel):
            raise ValueError("Invalid model file format")
        
        self.models[ml_model.model_name] = ml_model
        
        self.logger.info(f"Model {ml_model.model_name} loaded from {file_path}")
        
        return ml_model
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a trained model."""
        if model_name in self.models:
            del self.models[model_name]
            self.logger.info(f"Model {model_name} deleted")
            return True
        
        return False