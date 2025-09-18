"""
Machine Learning API routes.
"""

from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.application.services.ml_service import MLService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

# Initialize ML service
ml_service = MLService()


# Request/Response models
class TrainModelRequest(BaseModel):
    """Request model for training ML models."""
    model_type: str  # "classification", "regression", "clustering"
    target_column: Optional[str] = None
    model_name: Optional[str] = None
    n_clusters: Optional[int] = 3  # For clustering
    test_size: float = 0.2
    random_state: int = 42


class PredictRequest(BaseModel):
    """Request model for making predictions."""
    model_name: str
    data: List[Dict[str, Any]]


class ModelInfoResponse(BaseModel):
    """Response model for model information."""
    model_name: str
    model_type: str
    accuracy: Optional[float]
    metrics: Dict[str, Any]
    feature_columns: List[str]
    target_column: Optional[str]
    created_at: str


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    prediction: Any
    probability: Optional[float]
    confidence: Optional[float]
    model_info: Dict[str, Any]


class FeatureImportanceResponse(BaseModel):
    """Response model for feature importance."""
    feature_importance: Dict[str, float]
    model_name: str


@router.post("/train/classification")
async def train_classification_model(
    request: TrainModelRequest,
    csv_data: List[Dict[str, Any]]
):
    """Train a classification model."""
    try:
        if request.model_type != "classification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model type must be 'classification'"
            )
        
        if not request.target_column:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target column is required for classification"
            )
        
        # Convert data to DataFrame
        import pandas as pd
        df = pd.DataFrame(csv_data)
        
        # Train model
        model_name = request.model_name or f"classification_{request.target_column}"
        ml_model = await ml_service.train_classification_model(
            df=df,
            target_column=request.target_column,
            model_name=model_name,
            test_size=request.test_size,
            random_state=request.random_state
        )
        
        logger.info(f"Classification model {model_name} trained successfully")
        
        return {
            "success": True,
            "message": "Classification model trained successfully",
            "data": {
                "model_name": ml_model.model_name,
                "model_type": ml_model.model_type,
                "accuracy": ml_model.accuracy,
                "metrics": ml_model.metrics,
                "feature_columns": ml_model.feature_columns,
                "target_column": ml_model.target_column
            }
        }
        
    except Exception as e:
        logger.error(f"Error training classification model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to train classification model: {str(e)}"
        )


@router.post("/train/regression")
async def train_regression_model(
    request: TrainModelRequest,
    csv_data: List[Dict[str, Any]]
):
    """Train a regression model."""
    try:
        if request.model_type != "regression":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model type must be 'regression'"
            )
        
        if not request.target_column:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target column is required for regression"
            )
        
        # Convert data to DataFrame
        import pandas as pd
        df = pd.DataFrame(csv_data)
        
        # Train model
        model_name = request.model_name or f"regression_{request.target_column}"
        ml_model = await ml_service.train_regression_model(
            df=df,
            target_column=request.target_column,
            model_name=model_name,
            test_size=request.test_size,
            random_state=request.random_state
        )
        
        logger.info(f"Regression model {model_name} trained successfully")
        
        return {
            "success": True,
            "message": "Regression model trained successfully",
            "data": {
                "model_name": ml_model.model_name,
                "model_type": ml_model.model_type,
                "accuracy": ml_model.accuracy,  # R² score for regression
                "metrics": ml_model.metrics,
                "feature_columns": ml_model.feature_columns,
                "target_column": ml_model.target_column
            }
        }
        
    except Exception as e:
        logger.error(f"Error training regression model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to train regression model: {str(e)}"
        )


@router.post("/train/clustering")
async def train_clustering_model(
    request: TrainModelRequest,
    csv_data: List[Dict[str, Any]]
):
    """Train a clustering model."""
    try:
        if request.model_type != "clustering":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model type must be 'clustering'"
            )
        
        # Convert data to DataFrame
        import pandas as pd
        df = pd.DataFrame(csv_data)
        
        # Train model
        model_name = request.model_name or f"clustering_{request.n_clusters}_clusters"
        ml_model = await ml_service.train_clustering_model(
            df=df,
            n_clusters=request.n_clusters or 3,
            model_name=model_name,
            random_state=request.random_state
        )
        
        logger.info(f"Clustering model {model_name} trained successfully")
        
        return {
            "success": True,
            "message": "Clustering model trained successfully",
            "data": {
                "model_name": ml_model.model_name,
                "model_type": ml_model.model_type,
                "metrics": ml_model.metrics,
                "feature_columns": ml_model.feature_columns,
                "n_clusters": request.n_clusters
            }
        }
        
    except Exception as e:
        logger.error(f"Error training clustering model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to train clustering model: {str(e)}"
        )


@router.post("/predict", response_model=PredictionResponse)
async def make_prediction(request: PredictRequest):
    """Make predictions using a trained model."""
    try:
        # Convert data to DataFrame
        import pandas as pd
        df = pd.DataFrame(request.data)
        
        # Make prediction
        prediction = await ml_service.predict(request.model_name, df)
        
        logger.info(f"Prediction made using model {request.model_name}")
        
        return PredictionResponse(
            prediction=prediction.prediction,
            probability=prediction.probability,
            confidence=prediction.confidence,
            model_info=prediction.model_info
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to make prediction: {str(e)}"
        )


@router.get("/models", response_model=List[Dict[str, Any]])
async def list_models():
    """List all trained models."""
    try:
        models = await ml_service.list_models()
        
        return {
            "success": True,
            "data": models
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models"
        )


@router.get("/models/{model_name}", response_model=ModelInfoResponse)
async def get_model_info(model_name: str):
    """Get information about a specific model."""
    try:
        model_info = await ml_service.get_model_info(model_name)
        
        return ModelInfoResponse(**model_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model information"
        )


@router.get("/models/{model_name}/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance(
    model_name: str,
    top_n: int = Query(10, ge=1, le=50)
):
    """Get feature importance for a model."""
    try:
        importance = await ml_service.get_feature_importance(model_name, top_n)
        
        return FeatureImportanceResponse(
            feature_importance=importance,
            model_name=model_name
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feature importance"
        )


@router.post("/models/{model_name}/save")
async def save_model(model_name: str, file_path: Optional[str] = None):
    """Save a trained model to disk."""
    try:
        saved_path = await ml_service.save_model(model_name, file_path)
        
        return {
            "success": True,
            "message": f"Model {model_name} saved successfully",
            "data": {
                "model_name": model_name,
                "file_path": saved_path
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save model"
        )


@router.post("/models/load")
async def load_model(file_path: str):
    """Load a model from disk."""
    try:
        ml_model = await ml_service.load_model(file_path)
        
        return {
            "success": True,
            "message": f"Model {ml_model.model_name} loaded successfully",
            "data": {
                "model_name": ml_model.model_name,
                "model_type": ml_model.model_type,
                "accuracy": ml_model.accuracy
            }
        }
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load model: {str(e)}"
        )


@router.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """Delete a trained model."""
    try:
        success = await ml_service.delete_model(model_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_name} not found"
            )
        
        return {
            "success": True,
            "message": f"Model {model_name} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete model"
        )


@router.post("/prepare-data")
async def prepare_data_for_ml(
    csv_data: List[Dict[str, Any]],
    target_column: Optional[str] = None,
    feature_selection: bool = True
):
    """Prepare data for machine learning."""
    try:
        # Convert data to DataFrame
        import pandas as pd
        df = pd.DataFrame(csv_data)
        
        # Prepare data
        prepared_df, feature_columns, target = await ml_service.prepare_data_for_ml(
            df, target_column, feature_selection
        )
        
        # Convert back to list of dictionaries for JSON response
        prepared_data = prepared_df.to_dict('records')
        
        return {
            "success": True,
            "message": "Data prepared for ML successfully",
            "data": {
                "prepared_data": prepared_data,
                "feature_columns": feature_columns,
                "target_column": target,
                "original_shape": df.shape,
                "prepared_shape": prepared_df.shape
            }
        }
        
    except Exception as e:
        logger.error(f"Error preparing data for ML: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to prepare data: {str(e)}"
        )


@router.get("/recommendations")
async def get_ml_recommendations(
    csv_data: List[Dict[str, Any]],
    target_column: Optional[str] = None
):
    """Get ML model recommendations based on data analysis."""
    try:
        # Convert data to DataFrame
        import pandas as pd
        df = pd.DataFrame(csv_data)
        
        recommendations = []
        
        # Analyze data structure
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # Check for target column
        if target_column:
            if target_column in numeric_columns:
                # Numeric target - recommend regression
                recommendations.append({
                    "model_type": "regression",
                    "reason": "Target column is numeric",
                    "confidence": "high"
                })
            elif target_column in categorical_columns:
                # Categorical target - recommend classification
                unique_values = df[target_column].nunique()
                if unique_values == 2:
                    recommendations.append({
                        "model_type": "classification",
                        "subtype": "binary",
                        "reason": f"Binary target with {unique_values} classes",
                        "confidence": "high"
                    })
                elif 2 < unique_values <= 10:
                    recommendations.append({
                        "model_type": "classification",
                        "subtype": "multiclass",
                        "reason": f"Multiclass target with {unique_values} classes",
                        "confidence": "high"
                    })
                else:
                    recommendations.append({
                        "model_type": "classification",
                        "subtype": "multiclass",
                        "reason": f"Target has {unique_values} classes (consider grouping)",
                        "confidence": "medium"
                    })
        else:
            # No target - recommend clustering or unsupervised learning
            if len(numeric_columns) >= 2:
                recommendations.append({
                    "model_type": "clustering",
                    "reason": "No target column and multiple numeric features available",
                    "confidence": "high"
                })
            
            if len(categorical_columns) > 0:
                recommendations.append({
                    "model_type": "association_rules",
                    "reason": "Categorical data available for pattern mining",
                    "confidence": "medium"
                })
        
        # Additional recommendations based on data characteristics
        if len(df) < 100:
            recommendations.append({
                "model_type": "warning",
                "reason": "Small dataset - consider collecting more data",
                "confidence": "high"
            })
        
        if df.isnull().sum().sum() > len(df) * 0.1:
            recommendations.append({
                "model_type": "preprocessing",
                "reason": "High percentage of missing values - data cleaning recommended",
                "confidence": "high"
            })
        
        return {
            "success": True,
            "message": "ML recommendations generated successfully",
            "data": {
                "recommendations": recommendations,
                "data_summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "numeric_columns": len(numeric_columns),
                    "categorical_columns": len(categorical_columns),
                    "missing_values": df.isnull().sum().sum(),
                    "missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating ML recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )