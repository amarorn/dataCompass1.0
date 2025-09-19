"""
Chart generator service - generates data visualizations.
"""

import asyncio
import os
import tempfile
from typing import Any, Dict, List, Optional

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from app.core.logging import LoggerMixin
from app.infrastructure.external.whatsapp_service import WhatsAppService


class ChartGenerationResult:
    """Result of chart generation."""
    
    def __init__(
        self,
        success: bool,
        charts: List[str],
        message: str,
        error: Optional[str] = None
    ):
        self.success = success
        self.charts = charts
        self.message = message
        self.error = error


class ChartGeneratorService(LoggerMixin):
    """Service for generating data visualizations."""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self._setup_matplotlib()
    
    def _setup_matplotlib(self) -> None:
        """Setup matplotlib for chart generation."""
        plt.style.use('default')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['figure.dpi'] = 150
    
    async def generate_and_send_charts(
        self,
        message_id: str,
        filename: str,
        from_number: str,
        data: List[Dict[str, Any]]
    ) -> ChartGenerationResult:
        """Generate charts from data and send via WhatsApp."""
        try:
            self.logger.info(f"Generating charts for {filename} ({message_id})")
            
            if not data:
                return ChartGenerationResult(
                    success=False,
                    charts=[],
                    message="No data to generate charts",
                    error="Empty dataset"
                )
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Generate charts
            chart_paths = await self._generate_charts(df, filename, message_id)
            
            if not chart_paths:
                return ChartGenerationResult(
                    success=False,
                    charts=[],
                    message="Failed to generate charts",
                    error="Chart generation failed"
                )
            
            # Send charts via WhatsApp
            send_results = await self._send_charts_to_whatsapp(
                chart_paths, from_number, filename
            )
            
            # Clean up temporary files
            await self._cleanup_charts(chart_paths)
            
            success_count = sum(1 for result in send_results if result)
            
            return ChartGenerationResult(
                success=success_count > 0,
                charts=chart_paths,
                message=f"{success_count}/{len(chart_paths)} charts sent successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error generating and sending charts: {e}")
            return ChartGenerationResult(
                success=False,
                charts=[],
                message="Error generating charts",
                error=str(e)
            )
    
    async def _generate_charts(
        self,
        df: pd.DataFrame,
        filename: str,
        message_id: str
    ) -> List[str]:
        """Generate various charts from DataFrame."""
        chart_paths = []
        
        try:
            # Create temporary directory for charts
            temp_dir = tempfile.mkdtemp(prefix=f"charts_{message_id}_")
            
            # Get numeric and categorical columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            # 1. Distribution plots for numeric columns
            if numeric_cols:
                chart_path = await self._create_distribution_plots(
                    df, numeric_cols, filename, temp_dir
                )
                if chart_path:
                    chart_paths.append(chart_path)
            
            # 2. Correlation heatmap
            if len(numeric_cols) > 1:
                chart_path = await self._create_correlation_heatmap(
                    df, numeric_cols, filename, temp_dir
                )
                if chart_path:
                    chart_paths.append(chart_path)
            
            # 3. Categorical analysis
            if categorical_cols:
                chart_path = await self._create_categorical_plots(
                    df, categorical_cols, filename, temp_dir
                )
                if chart_path:
                    chart_paths.append(chart_path)
            
            # 4. Summary statistics
            chart_path = await self._create_summary_chart(
                df, filename, temp_dir
            )
            if chart_path:
                chart_paths.append(chart_path)
            
            # 5. Interactive plotly chart
            if numeric_cols:
                chart_path = await self._create_interactive_chart(
                    df, numeric_cols, filename, temp_dir
                )
                if chart_path:
                    chart_paths.append(chart_path)
            
            self.logger.info(f"Generated {len(chart_paths)} charts for {filename}")
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
        
        return chart_paths
    
    async def _create_distribution_plots(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
        filename: str,
        temp_dir: str
    ) -> Optional[str]:
        """Create distribution plots for numeric columns."""
        try:
            n_cols = min(len(numeric_cols), 4)
            n_rows = (len(numeric_cols) + 1) // 2
            
            fig, axes = plt.subplots(n_rows, 2, figsize=(15, 4 * n_rows))
            if n_rows == 1:
                axes = axes.reshape(1, -1)
            
            fig.suptitle(f'Distribuições - {filename}', fontsize=16, y=0.98)
            
            for i, col in enumerate(numeric_cols[:4]):
                row, col_idx = i // 2, i % 2
                ax = axes[row, col_idx]
                
                # Histogram
                df[col].hist(bins=20, ax=ax, alpha=0.7, edgecolor='black', color='skyblue')
                ax.set_title(f'Distribuição: {col}')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequência')
                
                # Add statistics
                mean_val = df[col].mean()
                median_val = df[col].median()
                ax.axvline(mean_val, color='red', linestyle='--', alpha=0.8, 
                          label=f'Média: {mean_val:.2f}')
                ax.axvline(median_val, color='green', linestyle='--', alpha=0.8, 
                          label=f'Mediana: {median_val:.2f}')
                ax.legend(fontsize=8)
            
            # Remove empty subplots
            for i in range(len(numeric_cols), n_rows * 2):
                row, col_idx = i // 2, i % 2
                fig.delaxes(axes[row, col_idx])
            
            plt.tight_layout()
            
            chart_path = os.path.join(temp_dir, 'distribuicoes_numericas.png')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Error creating distribution plots: {e}")
            return None
    
    async def _create_correlation_heatmap(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
        filename: str,
        temp_dir: str
    ) -> Optional[str]:
        """Create correlation heatmap."""
        try:
            fig, ax = plt.subplots(1, 1, figsize=(10, 8))
            
            correlation_matrix = df[numeric_cols].corr()
            
            # Heatmap
            mask = None
            if len(numeric_cols) > 2:
                import numpy as np
                mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            
            sns.heatmap(
                correlation_matrix,
                mask=mask,
                annot=True,
                cmap='coolwarm',
                center=0,
                square=True,
                fmt='.2f',
                cbar_kws={"shrink": .8},
                ax=ax
            )
            ax.set_title(f'Matriz de Correlação - {filename}')
            plt.tight_layout()
            
            chart_path = os.path.join(temp_dir, 'matriz_correlacao.png')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Error creating correlation heatmap: {e}")
            return None
    
    async def _create_categorical_plots(
        self,
        df: pd.DataFrame,
        categorical_cols: List[str],
        filename: str,
        temp_dir: str
    ) -> Optional[str]:
        """Create categorical plots."""
        try:
            n_cat_plots = min(len(categorical_cols), 4)
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            axes = axes.flatten()
            
            fig.suptitle(f'Variáveis Categóricas - {filename}', fontsize=16)
            
            for i, col in enumerate(categorical_cols[:4]):
                ax = axes[i]
                
                # Top 10 values
                top_values = df[col].value_counts().head(10)
                
                # Bar plot
                top_values.plot(kind='bar', ax=ax, color='lightcoral', alpha=0.8)
                ax.set_title(f'{col} (Top 10)')
                ax.set_xlabel('')
                ax.set_ylabel('Contagem')
                ax.tick_params(axis='x', rotation=45)
                
                # Add values on bars
                for j, v in enumerate(top_values.values):
                    ax.text(j, v + 0.1, str(v), ha='center', va='bottom', fontsize=8)
            
            # Remove empty subplots
            for i in range(len(categorical_cols), 4):
                fig.delaxes(axes[i])
            
            plt.tight_layout()
            
            chart_path = os.path.join(temp_dir, 'variaveis_categoricas.png')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Error creating categorical plots: {e}")
            return None
    
    async def _create_summary_chart(
        self,
        df: pd.DataFrame,
        filename: str,
        temp_dir: str
    ) -> Optional[str]:
        """Create summary statistics chart."""
        try:
            # Create a summary with key statistics
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Resumo Executivo - {filename}', fontsize=16)
            
            # Basic info
            ax1.text(0.1, 0.8, f'Total de registros: {len(df)}', fontsize=12, transform=ax1.transAxes)
            ax1.text(0.1, 0.6, f'Total de colunas: {len(df.columns)}', fontsize=12, transform=ax1.transAxes)
            ax1.text(0.1, 0.4, f'Valores ausentes: {df.isnull().sum().sum()}', fontsize=12, transform=ax1.transAxes)
            ax1.text(0.1, 0.2, f'Duplicatas: {df.duplicated().sum()}', fontsize=12, transform=ax1.transAxes)
            ax1.set_title('Informações Gerais')
            ax1.axis('off')
            
            # Data types
            dtype_counts = df.dtypes.value_counts()
            ax2.pie(dtype_counts.values, labels=dtype_counts.index, autopct='%1.1f%%')
            ax2.set_title('Tipos de Dados')
            
            # Missing values
            missing = df.isnull().sum()
            if missing.sum() > 0:
                missing = missing[missing > 0]
                ax3.barh(range(len(missing)), missing.values)
                ax3.set_yticks(range(len(missing)))
                ax3.set_yticklabels(missing.index)
                ax3.set_xlabel('Valores Ausentes')
                ax3.set_title('Valores Ausentes por Coluna')
            else:
                ax3.text(0.5, 0.5, 'Nenhum valor ausente', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Valores Ausentes')
            
            # Memory usage
            memory_usage = df.memory_usage(deep=True) / 1024  # KB
            ax4.barh(range(len(memory_usage)), memory_usage.values)
            ax4.set_yticks(range(len(memory_usage)))
            ax4.set_yticklabels(memory_usage.index)
            ax4.set_xlabel('Uso de Memória (KB)')
            ax4.set_title('Uso de Memória por Coluna')
            
            plt.tight_layout()
            
            chart_path = os.path.join(temp_dir, 'resumo_executivo.png')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Error creating summary chart: {e}")
            return None
    
    async def _create_interactive_chart(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
        filename: str,
        temp_dir: str
    ) -> Optional[str]:
        """Create interactive plotly chart."""
        try:
            if len(numeric_cols) >= 2:
                # Scatter plot
                fig = px.scatter(
                    df,
                    x=numeric_cols[0],
                    y=numeric_cols[1],
                    title=f'Relação entre {numeric_cols[0]} e {numeric_cols[1]} - {filename}',
                    labels={numeric_cols[0]: numeric_cols[0], numeric_cols[1]: numeric_cols[1]}
                )
            else:
                # Histogram
                fig = px.histogram(
                    df,
                    x=numeric_cols[0],
                    title=f'Distribuição de {numeric_cols[0]} - {filename}'
                )
            
            chart_path = os.path.join(temp_dir, 'grafico_interativo.html')
            fig.write_html(chart_path)
            
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Error creating interactive chart: {e}")
            return None
    
    async def _send_charts_to_whatsapp(
        self,
        chart_paths: List[str],
        to: str,
        filename: str
    ) -> List[bool]:
        """Send charts via WhatsApp."""
        results = []
        
        # Send intro message
        intro_message = f"""📊 *Análise Exploratória Concluída!*

📄 *Arquivo:* {filename}
📈 *Gráficos gerados:* {len(chart_paths)}

Os gráficos com insights detalhados serão enviados a seguir:"""
        
        try:
            await self.whatsapp_service.send_text_message(to, intro_message)
            self.logger.info("Intro message sent")
        except Exception as e:
            self.logger.error(f"Error sending intro message: {e}")
        
        # Wait before sending charts
        await asyncio.sleep(2)
        
        # Send each chart
        for i, chart_path in enumerate(chart_paths):
            try:
                # Determine caption based on filename
                caption = self._get_chart_caption(chart_path, i + 1, len(chart_paths))
                
                # Send chart
                if chart_path.endswith('.html'):
                    # For HTML files, send as document
                    success = await self.whatsapp_service.send_document(to, chart_path, caption)
                else:
                    # For images, send as document
                    success = await self.whatsapp_service.send_document(to, chart_path, caption)
                
                results.append(success)
                
                if success:
                    self.logger.info(f"Chart {i + 1}/{len(chart_paths)} sent successfully")
                else:
                    self.logger.error(f"Failed to send chart {i + 1}/{len(chart_paths)}")
                
                # Wait between sends
                if i < len(chart_paths) - 1:
                    await asyncio.sleep(3)
                    
            except Exception as e:
                self.logger.error(f"Error sending chart {chart_path}: {e}")
                results.append(False)
        
        # Send final message
        success_count = sum(results)
        final_message = f"""✅ *Análise Concluída!*

📊 *Gráficos enviados:* {success_count}/{len(chart_paths)}
🎯 *Status:* {"Todos enviados com sucesso!" if success_count == len(chart_paths) else "Alguns gráficos falharam"}

💡 *Dica:* Use estes insights para tomar decisões baseadas em dados!"""
        
        try:
            await self.whatsapp_service.send_text_message(to, final_message)
            self.logger.info("Final message sent")
        except Exception as e:
            self.logger.error(f"Error sending final message: {e}")
        
        return results
    
    def _get_chart_caption(self, chart_path: str, index: int, total: int) -> str:
        """Get caption for chart based on filename."""
        filename = os.path.basename(chart_path)
        
        if 'distribuicoes' in filename:
            return '📊 *Distribuições das Variáveis*\n\nEste gráfico mostra a distribuição de cada variável numérica com média e mediana destacadas.'
        elif 'correlacao' in filename:
            return '🔗 *Matriz de Correlação*\n\nMostra as correlações entre variáveis numéricas. Valores próximos a 1 ou -1 indicam forte correlação.'
        elif 'categoricas' in filename:
            return '📊 *Variáveis Categóricas*\n\nDistribuição de frequência das principais categorias em cada variável categórica.'
        elif 'resumo' in filename:
            return '📈 *Resumo Executivo*\n\nVisão geral dos principais indicadores e métricas do seu dataset.'
        elif 'interativo' in filename:
            return '🎯 *Gráfico Interativo*\n\nVisualização interativa que você pode explorar em detalhes.'
        else:
            return f'📊 Gráfico {index} de {total}'
    
    async def _cleanup_charts(self, chart_paths: List[str]) -> None:
        """Clean up temporary chart files."""
        for chart_path in chart_paths:
            try:
                if os.path.exists(chart_path):
                    os.remove(chart_path)
                    self.logger.debug(f"Removed temporary file: {chart_path}")
            except Exception as e:
                self.logger.warning(f"Could not remove temporary file {chart_path}: {e}")
        
        # Remove temporary directory if empty
        try:
            temp_dir = os.path.dirname(chart_paths[0]) if chart_paths else None
            if temp_dir and temp_dir.startswith('/tmp/charts_'):
                if not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
                    self.logger.debug(f"Removed temporary directory: {temp_dir}")
        except Exception as e:
            self.logger.warning(f"Could not remove temporary directory: {e}")