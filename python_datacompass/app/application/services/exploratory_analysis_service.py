"""
Exploratory analysis service - performs comprehensive data analysis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from app.core.logging import LoggerMixin


class DataStructure:
    """Data structure analysis result."""
    
    def __init__(
        self,
        total_columns: int,
        column_types: Dict[str, str],
        feature_distribution: Dict[str, List[str]]
    ):
        self.total_columns = total_columns
        self.column_types = column_types
        self.feature_distribution = feature_distribution


class DataQuality:
    """Data quality analysis result."""
    
    def __init__(
        self,
        overall_score: float,
        completeness: Dict[str, Any],
        consistency: Dict[str, Any],
        validity: Dict[str, Any]
    ):
        self.overall_score = overall_score
        self.completeness = completeness
        self.consistency = consistency
        self.validity = validity


class DescriptiveStats:
    """Descriptive statistics result."""
    
    def __init__(
        self,
        numeric: Dict[str, Dict[str, Any]],
        categorical: Dict[str, Dict[str, Any]],
        text: Dict[str, Dict[str, Any]],
        date: Dict[str, Dict[str, Any]]
    ):
        self.numeric = numeric
        self.categorical = categorical
        self.text = text
        self.date = date


class Relationships:
    """Relationships analysis result."""
    
    def __init__(
        self,
        correlation_matrix: Optional[Dict[str, Dict[str, float]]],
        strong_correlations: List[Dict[str, Any]]
    ):
        self.correlation_matrix = correlation_matrix
        self.strong_correlations = strong_correlations


class Insights:
    """Insights result."""
    
    def __init__(
        self,
        key_findings: List[str],
        data_quality_issues: List[str],
        recommendations: List[str],
        potential_ml_features: List[str],
        business_insights: List[str]
    ):
        self.key_findings = key_findings
        self.data_quality_issues = data_quality_issues
        self.recommendations = recommendations
        self.potential_ml_features = potential_ml_features
        self.business_insights = business_insights


class SuggestedVisualization:
    """Suggested visualization."""
    
    def __init__(
        self,
        chart_type: str,
        features: List[str],
        description: str,
        priority: str
    ):
        self.chart_type = chart_type
        self.features = features
        self.description = description
        self.priority = priority


class ExploratoryAnalysisResult:
    """Complete exploratory analysis result."""
    
    def __init__(
        self,
        message_id: str,
        filename: str,
        from_number: str,
        total_records: int,
        analysis_date: datetime,
        data_structure: DataStructure,
        data_quality: DataQuality,
        descriptive_stats: DescriptiveStats,
        relationships: Relationships,
        insights: Insights,
        suggested_visualizations: List[SuggestedVisualization]
    ):
        self.message_id = message_id
        self.filename = filename
        self.from_number = from_number
        self.total_records = total_records
        self.analysis_date = analysis_date
        self.data_structure = data_structure
        self.data_quality = data_quality
        self.descriptive_stats = descriptive_stats
        self.relationships = relationships
        self.insights = insights
        self.suggested_visualizations = suggested_visualizations


class ExploratoryAnalysisService(LoggerMixin):
    """Service for performing exploratory data analysis."""
    
    async def perform_exploratory_analysis(
        self,
        message_id: str,
        filename: str,
        from_number: str,
        raw_data: List[Dict[str, Any]]
    ) -> ExploratoryAnalysisResult:
        """Perform comprehensive exploratory analysis."""
        self.logger.info(f"Starting exploratory analysis for {filename} ({len(raw_data)} records)")
        
        analysis_date = datetime.utcnow()
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data)
        
        # 1. Analyze data structure
        data_structure = self._analyze_data_structure(df)
        
        # 2. Analyze data quality
        data_quality = self._analyze_data_quality(df, data_structure.column_types)
        
        # 3. Calculate descriptive statistics
        descriptive_stats = self._calculate_descriptive_statistics(df, data_structure)
        
        # 4. Analyze relationships
        relationships = self._analyze_relationships(df, data_structure)
        
        # 5. Generate insights
        insights = self._generate_insights(df, data_structure, data_quality, descriptive_stats)
        
        # 6. Suggest visualizations
        suggested_visualizations = self._suggest_visualizations(data_structure, descriptive_stats)
        
        result = ExploratoryAnalysisResult(
            message_id=message_id,
            filename=filename,
            from_number=from_number,
            total_records=len(df),
            analysis_date=analysis_date,
            data_structure=data_structure,
            data_quality=data_quality,
            descriptive_stats=descriptive_stats,
            relationships=relationships,
            insights=insights,
            suggested_visualizations=suggested_visualizations
        )
        
        self.logger.info(f"Exploratory analysis completed for {filename}")
        return result
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> DataStructure:
        """Analyze data structure."""
        if df.empty:
            return DataStructure(0, {}, {
                "numeric": [], "categorical": [], "text": [], "date": [], "boolean": []
            })
        
        columns = df.columns.tolist()
        column_types = {}
        feature_distribution = {
            "numeric": [],
            "categorical": [],
            "text": [],
            "date": [],
            "boolean": []
        }
        
        for column in columns:
            data_type = self._detect_data_type(df[column])
            column_types[column] = data_type
            feature_distribution[data_type].append(column)
        
        return DataStructure(
            total_columns=len(columns),
            column_types=column_types,
            feature_distribution=feature_distribution
        )
    
    def _detect_data_type(self, series: pd.Series) -> str:
        """Detect data type of a pandas Series."""
        if series.empty:
            return "text"
        
        # Remove null values for analysis
        values = series.dropna()
        
        if len(values) == 0:
            return "text"
        
        # Check for boolean
        boolean_values = values.astype(str).str.lower().isin(
            ['true', 'false', '1', '0', 'sim', 'não', 'yes', 'no']
        )
        if boolean_values.sum() > len(values) * 0.8:
            return "boolean"
        
        # Check for numeric
        try:
            numeric_values = pd.to_numeric(values, errors='coerce')
            if numeric_values.notna().sum() > len(values) * 0.8:
                return "numeric"
        except:
            pass
        
        # Check for date
        try:
            date_values = pd.to_datetime(values, errors='coerce')
            if date_values.notna().sum() > len(values) * 0.6:
                return "date"
        except:
            pass
        
        # Check for categorical (few unique values)
        unique_values = values.nunique()
        unique_ratio = unique_values / len(values)
        
        if unique_ratio < 0.1 and unique_values < 50:
            return "categorical"
        
        return "text"
    
    def _analyze_data_quality(
        self, 
        df: pd.DataFrame, 
        column_types: Dict[str, str]
    ) -> DataQuality:
        """Analyze data quality."""
        columns = list(column_types.keys())
        total_cells = len(df) * len(columns)
        
        # Completeness analysis
        missing_values = {}
        completeness_per_column = {}
        total_missing = 0
        
        for column in columns:
            missing = df[column].isnull().sum()
            missing_values[column] = int(missing)
            completeness_per_column[column] = (len(df) - missing) / len(df)
            total_missing += missing
        
        completeness_score = (total_cells - total_missing) / total_cells
        
        # Consistency analysis
        inconsistent_values = {}
        consistency_issues = 0
        
        for column in columns:
            expected_type = column_types[column]
            inconsistent = []
            
            for value in df[column].dropna():
                if not self._is_value_consistent_with_type(value, expected_type):
                    inconsistent.append(str(value))
                    consistency_issues += 1
            
            if inconsistent:
                inconsistent_values[column] = list(set(inconsistent))[:10]
        
        consistency_score = max(0, (total_cells - total_missing - consistency_issues) / (total_cells - total_missing)) if (total_cells - total_missing) > 0 else 1.0
        
        # Validity analysis
        invalid_values = {}
        total_invalid = 0
        
        for column in columns:
            invalid = 0
            for value in df[column].dropna():
                if not self._is_valid_value(value, column_types[column]):
                    invalid += 1
            
            invalid_values[column] = invalid
            total_invalid += invalid
        
        validity_score = (total_cells - total_missing - total_invalid) / (total_cells - total_missing) if (total_cells - total_missing) > 0 else 1.0
        
        overall_score = (completeness_score + consistency_score + validity_score) / 3
        
        return DataQuality(
            overall_score=round(overall_score, 3),
            completeness={
                "score": round(completeness_score, 3),
                "missing_values": missing_values,
                "completeness_per_column": completeness_per_column
            },
            consistency={
                "score": round(consistency_score, 3),
                "inconsistent_values": inconsistent_values
            },
            validity={
                "score": round(validity_score, 3),
                "invalid_values": invalid_values
            }
        )
    
    def _is_value_consistent_with_type(self, value: Any, data_type: str) -> bool:
        """Check if value is consistent with expected data type."""
        try:
            if data_type == "numeric":
                return not pd.isna(pd.to_numeric(value))
            elif data_type == "boolean":
                return str(value).lower() in ['true', 'false', '1', '0', 'sim', 'não', 'yes', 'no']
            elif data_type == "date":
                return not pd.isna(pd.to_datetime(value))
            else:
                return True
        except:
            return False
    
    def _is_valid_value(self, value: Any, data_type: str) -> bool:
        """Check if value is valid for its data type."""
        if pd.isna(value) or value == "":
            return False
        return self._is_value_consistent_with_type(value, data_type)
    
    def _calculate_descriptive_statistics(
        self, 
        df: pd.DataFrame, 
        data_structure: DataStructure
    ) -> DescriptiveStats:
        """Calculate descriptive statistics."""
        numeric_stats = {}
        categorical_stats = {}
        text_stats = {}
        date_stats = {}
        
        # Numeric statistics
        for column in data_structure.feature_distribution["numeric"]:
            values = pd.to_numeric(df[column], errors='coerce').dropna()
            if len(values) > 0:
                numeric_stats[column] = {
                    "count": len(values),
                    "mean": round(float(values.mean()), 3),
                    "median": round(float(values.median()), 3),
                    "std": round(float(values.std()), 3),
                    "variance": round(float(values.var()), 3),
                    "min": round(float(values.min()), 3),
                    "max": round(float(values.max()), 3),
                    "q1": round(float(values.quantile(0.25)), 3),
                    "q3": round(float(values.quantile(0.75)), 3),
                    "iqr": round(float(values.quantile(0.75) - values.quantile(0.25)), 3),
                    "skewness": round(float(values.skew()), 3),
                    "kurtosis": round(float(values.kurtosis()), 3),
                    "outliers": self._detect_outliers(values).tolist()[:10]
                }
        
        # Categorical statistics
        for column in data_structure.feature_distribution["categorical"]:
            values = df[column].dropna()
            if len(values) > 0:
                value_counts = values.value_counts()
                categorical_stats[column] = {
                    "count": len(values),
                    "unique_values": values.nunique(),
                    "most_frequent": {
                        "value": str(value_counts.index[0]),
                        "frequency": int(value_counts.iloc[0])
                    },
                    "least_frequent": {
                        "value": str(value_counts.index[-1]),
                        "frequency": int(value_counts.iloc[-1])
                    },
                    "value_distribution": [
                        {
                            "value": str(val),
                            "count": int(count),
                            "percentage": round((count / len(values)) * 100, 2)
                        }
                        for val, count in value_counts.head(10).items()
                    ],
                    "entropy": round(self._calculate_entropy(value_counts.values), 3)
                }
        
        # Text statistics
        for column in data_structure.feature_distribution["text"]:
            values = df[column].astype(str).dropna()
            if len(values) > 0:
                lengths = values.str.len()
                text_stats[column] = {
                    "count": len(values),
                    "avg_length": round(float(lengths.mean()), 2),
                    "min_length": int(lengths.min()),
                    "max_length": int(lengths.max()),
                    "unique_values": values.nunique()
                }
        
        # Date statistics
        for column in data_structure.feature_distribution["date"]:
            dates = pd.to_datetime(df[column], errors='coerce').dropna()
            if len(dates) > 0:
                date_stats[column] = {
                    "count": len(dates),
                    "earliest_date": dates.min().isoformat(),
                    "latest_date": dates.max().isoformat(),
                    "date_range": (dates.max() - dates.min()).days
                }
        
        return DescriptiveStats(
            numeric=numeric_stats,
            categorical=categorical_stats,
            text=text_stats,
            date=date_stats
        )
    
    def _detect_outliers(self, values: pd.Series) -> pd.Series:
        """Detect outliers using IQR method."""
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return values[(values < lower_bound) | (values > upper_bound)]
    
    def _calculate_entropy(self, frequencies: np.ndarray) -> float:
        """Calculate entropy of a distribution."""
        total = np.sum(frequencies)
        if total == 0:
            return 0
        
        probabilities = frequencies / total
        probabilities = probabilities[probabilities > 0]  # Remove zero probabilities
        
        return -np.sum(probabilities * np.log2(probabilities))
    
    def _analyze_relationships(
        self, 
        df: pd.DataFrame, 
        data_structure: DataStructure
    ) -> Relationships:
        """Analyze relationships between variables."""
        numeric_features = data_structure.feature_distribution["numeric"]
        correlation_matrix = {}
        strong_correlations = []
        
        if len(numeric_features) > 1:
            # Calculate correlation matrix
            numeric_df = df[numeric_features].select_dtypes(include=[np.number])
            correlation_matrix = numeric_df.corr().to_dict()
            
            # Find strong correlations
            for i, feature1 in enumerate(numeric_features):
                for j, feature2 in enumerate(numeric_features):
                    if i < j:  # Avoid duplicates
                        try:
                            correlation = correlation_matrix[feature1][feature2]
                            if abs(correlation) > 0.5:
                                strong_correlations.append({
                                    "feature1": feature1,
                                    "feature2": feature2,
                                    "correlation": round(correlation, 3),
                                    "type": "positive" if correlation > 0 else "negative"
                                })
                        except KeyError:
                            continue
        
        return Relationships(
            correlation_matrix=correlation_matrix if correlation_matrix else None,
            strong_correlations=strong_correlations
        )
    
    def _generate_insights(
        self,
        df: pd.DataFrame,
        data_structure: DataStructure,
        data_quality: DataQuality,
        descriptive_stats: DescriptiveStats
    ) -> Insights:
        """Generate insights from the analysis."""
        key_findings = []
        data_quality_issues = []
        recommendations = []
        potential_ml_features = []
        business_insights = []
        
        # Key findings
        key_findings.append(f"Dataset contém {len(df)} registros e {data_structure.total_columns} colunas")
        key_findings.append(f"Qualidade geral dos dados: {(data_quality.overall_score * 100):.1f}%")
        
        if data_structure.feature_distribution["numeric"]:
            key_findings.append(f"{len(data_structure.feature_distribution['numeric'])} variáveis numéricas identificadas")
        
        if data_structure.feature_distribution["categorical"]:
            key_findings.append(f"{len(data_structure.feature_distribution['categorical'])} variáveis categóricas identificadas")
        
        # Data quality issues
        if data_quality.completeness["score"] < 0.9:
            data_quality_issues.append(f"Completude baixa: {(data_quality.completeness['score'] * 100):.1f}%")
        
        if data_quality.consistency["score"] < 0.9:
            data_quality_issues.append(f"Inconsistência nos dados: {(data_quality.consistency['score'] * 100):.1f}%")
        
        # Recommendations
        if len(data_structure.feature_distribution["numeric"]) > 2:
            recommendations.append("Considere análise de correlação entre variáveis numéricas")
        
        if data_quality.overall_score < 0.8:
            recommendations.append("Recomenda-se limpeza e pré-processamento dos dados")
        
        # Potential ML features
        for feature in data_structure.feature_distribution["numeric"]:
            if feature in descriptive_stats.numeric:
                stats = descriptive_stats.numeric[feature]
                if abs(stats.get("skewness", 0)) < 2:
                    potential_ml_features.append(f"{feature} (distribuição normal)")
        
        for feature in data_structure.feature_distribution["categorical"]:
            if feature in descriptive_stats.categorical:
                stats = descriptive_stats.categorical[feature]
                if 1 < stats.get("unique_values", 0) < 20:
                    potential_ml_features.append(f"{feature} (categórica balanceada)")
        
        return Insights(
            key_findings=key_findings,
            data_quality_issues=data_quality_issues,
            recommendations=recommendations,
            potential_ml_features=potential_ml_features,
            business_insights=business_insights
        )
    
    def _suggest_visualizations(
        self,
        data_structure: DataStructure,
        descriptive_stats: DescriptiveStats
    ) -> List[SuggestedVisualization]:
        """Suggest visualizations based on data structure."""
        suggestions = []
        
        # Histograms for numeric variables
        for feature in data_structure.feature_distribution["numeric"]:
            suggestions.append(SuggestedVisualization(
                chart_type="histogram",
                features=[feature],
                description=f"Distribuição de {feature}",
                priority="high"
            ))
        
        # Boxplots for outlier detection
        if data_structure.feature_distribution["numeric"]:
            suggestions.append(SuggestedVisualization(
                chart_type="boxplot",
                features=data_structure.feature_distribution["numeric"],
                description="Detecção de outliers em variáveis numéricas",
                priority="medium"
            ))
        
        # Bar charts for categorical variables
        for feature in data_structure.feature_distribution["categorical"]:
            suggestions.append(SuggestedVisualization(
                chart_type="bar",
                features=[feature],
                description=f"Distribuição de frequência de {feature}",
                priority="medium"
            ))
        
        # Scatter plots for correlations
        numeric_features = data_structure.feature_distribution["numeric"]
        if len(numeric_features) > 1:
            for i in range(len(numeric_features) - 1):
                for j in range(i + 1, len(numeric_features)):
                    suggestions.append(SuggestedVisualization(
                        chart_type="scatter",
                        features=[numeric_features[i], numeric_features[j]],
                        description=f"Correlação entre {numeric_features[i]} e {numeric_features[j]}",
                        priority="low"
                    ))
        
        # Correlation heatmap
        if len(numeric_features) > 2:
            suggestions.append(SuggestedVisualization(
                chart_type="heatmap",
                features=numeric_features,
                description="Matriz de correlação das variáveis numéricas",
                priority="high"
            ))
        
        return suggestions