#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Exploratória Avançada com Pandas - DataCompass
Análise dos dados CSV recebidos via WhatsApp
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from pymongo import MongoClient
import warnings
from datetime import datetime
import json

# Configurações
warnings.filterwarnings('ignore')
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_data_from_api():
    """Carrega dados da API e converte para DataFrame pandas"""
    print("🔍 CARREGANDO DADOS DA API")
    print("=" * 30)
    
    try:
        # Buscar lista de datasets
        response = requests.get("http://localhost:3000/api/whatsapp/raw")
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code}")
            return None, None
        
        data = response.json()
        if not data.get('success') or not data.get('data'):
            print("❌ Nenhum dataset encontrado")
            return None, None
        
        datasets = data['data']
        print(f"📊 Encontrados {len(datasets)} datasets")
        
        # Carregar o primeiro dataset
        dataset = datasets[0]
        message_id = dataset['messageId']
        
        print(f"📄 Carregando: {dataset['filename']}")
        print(f"📈 Registros: {dataset['recordCount']}")
        
        # Buscar dados detalhados
        detail_response = requests.get(f"http://localhost:3000/api/whatsapp/raw/{message_id}")
        if detail_response.status_code != 200:
            print(f"❌ Erro ao buscar detalhes: {detail_response.status_code}")
            return None, None
        
        detail_data = detail_response.json()
        if not detail_data.get('success'):
            print(f"❌ Erro nos dados: {detail_data.get('message')}")
            return None, None
        
        # Extrair dados normalizados dos registros
        records = detail_data['data']['records']
        
        # Criar DataFrame a partir dos dados normalizados
        normalized_data = []
        for record in records:
            normalized_data.append(record['normalizedData'])
        
        df = pd.DataFrame(normalized_data)
        
        # Converter coluna de data
        if 'data_venda' in df.columns:
            df['data_venda'] = pd.to_datetime(df['data_venda'])
        
        print(f"✅ DataFrame criado: {df.shape[0]} linhas x {df.shape[1]} colunas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        return df, dataset
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def perform_exploratory_analysis(df, dataset_info):
    """Realiza análise exploratória completa com pandas"""
    print(f"\n📊 ANÁLISE EXPLORATÓRIA DETALHADA")
    print("=" * 50)
    
    # Informações básicas
    print("1️⃣ INFORMAÇÕES GERAIS:")
    print(f"   • Dataset: {dataset_info['filename']}")
    print(f"   • Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print(f"   • Memória: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print(f"   • Origem: WhatsApp {dataset_info['from']}")
    
    # Tipos de dados
    print(f"\n2️⃣ TIPOS DE DADOS:")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    print(f"   • Numéricas ({len(numeric_cols)}): {numeric_cols}")
    print(f"   • Categóricas ({len(categorical_cols)}): {categorical_cols}")
    print(f"   • Data/Hora ({len(datetime_cols)}): {datetime_cols}")
    
    # Valores ausentes
    print(f"\n3️⃣ QUALIDADE DOS DADOS:")
    missing = df.isnull().sum()
    total_missing = missing.sum()
    missing_pct = (total_missing / df.size) * 100
    
    print(f"   • Valores ausentes: {total_missing} ({missing_pct:.1f}%)")
    print(f"   • Duplicatas: {df.duplicated().sum()}")
    print(f"   • Completude geral: {((df.count().sum() / df.size) * 100):.1f}%")
    
    if total_missing > 0:
        print("   • Por coluna:")
        for col in missing[missing > 0].index:
            pct = (missing[col] / len(df)) * 100
            print(f"     - {col}: {missing[col]} ({pct:.1f}%)")
    
    # Estatísticas descritivas
    if len(numeric_cols) > 0:
        print(f"\n4️⃣ ESTATÍSTICAS NUMÉRICAS:")
        print(df[numeric_cols].describe())
        
        # Análise individual de cada coluna numérica
        print(f"\n📊 ANÁLISE DETALHADA POR VARIÁVEL:")
        for col in numeric_cols:
            print(f"\n   📈 {col.upper()}:")
            data = df[col].dropna()
            
            if len(data) > 0:
                print(f"      • Média: {data.mean():.2f}")
                print(f"      • Mediana: {data.median():.2f}")
                print(f"      • Desvio padrão: {data.std():.2f}")
                print(f"      • Coef. variação: {(data.std()/data.mean()*100):.1f}%")
                print(f"      • Min/Max: {data.min():.2f} / {data.max():.2f}")
                print(f"      • Q1/Q3: {data.quantile(0.25):.2f} / {data.quantile(0.75):.2f}")
                
                # Detecção de outliers (IQR)
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = data[(data < lower_bound) | (data > upper_bound)]
                
                if len(outliers) > 0:
                    print(f"      • Outliers: {len(outliers)} ({len(outliers)/len(data)*100:.1f}%)")
                    print(f"        Valores: {outliers.head(3).tolist()}")
    
    # Análise categórica
    if len(categorical_cols) > 0:
        print(f"\n5️⃣ ANÁLISE CATEGÓRICA:")
        for col in categorical_cols:
            unique_count = df[col].nunique()
            print(f"\n   🏷️ {col.upper()}:")
            print(f"      • Valores únicos: {unique_count}")
            print(f"      • Cardinalidade: {unique_count/len(df)*100:.1f}%")
            
            if unique_count <= 10:
                print("      • Distribuição:")
                value_counts = df[col].value_counts()
                for val, count in value_counts.head(5).items():
                    pct = (count / len(df)) * 100
                    print(f"        - {val}: {count} ({pct:.1f}%)")
            else:
                print("      • Top 5 valores:")
                value_counts = df[col].value_counts()
                for val, count in value_counts.head(5).items():
                    pct = (count / len(df)) * 100
                    print(f"        - {val}: {count} ({pct:.1f}%)")
    
    # Análise temporal (se houver colunas de data)
    if len(datetime_cols) > 0:
        print(f"\n6️⃣ ANÁLISE TEMPORAL:")
        for col in datetime_cols:
            print(f"\n   📅 {col.upper()}:")
            date_data = df[col].dropna()
            if len(date_data) > 0:
                print(f"      • Período: {date_data.min()} até {date_data.max()}")
                print(f"      • Intervalo: {(date_data.max() - date_data.min()).days} dias")
                
                # Distribuição por dia da semana
                if len(date_data) > 1:
                    weekday_counts = date_data.dt.day_name().value_counts()
                    print("      • Por dia da semana:")
                    for day, count in weekday_counts.head(3).items():
                        pct = (count / len(date_data)) * 100
                        print(f"        - {day}: {count} ({pct:.1f}%)")
    
    return df

def create_visualizations(df, dataset_info):
    """Cria visualizações usando matplotlib e seaborn"""
    print(f"\n🎨 CRIANDO VISUALIZAÇÕES")
    print("=" * 30)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Configurar estilo
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 1. Distribuições das variáveis numéricas
    if len(numeric_cols) > 0:
        n_cols = min(len(numeric_cols), 4)
        n_rows = (len(numeric_cols) + 1) // 2
        
        fig, axes = plt.subplots(n_rows, 2, figsize=(15, 4 * n_rows))
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        fig.suptitle(f'Distribuições - {dataset_info["filename"]}', fontsize=16, y=0.98)
        
        for i, col in enumerate(numeric_cols[:4]):
            row, col_idx = i // 2, i % 2
            ax = axes[row, col_idx]
            
            # Histograma
            df[col].hist(bins=20, ax=ax, alpha=0.7, edgecolor='black', color='skyblue')
            ax.set_title(f'Distribuição: {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Frequência')
            
            # Estatísticas no gráfico
            mean_val = df[col].mean()
            median_val = df[col].median()
            ax.axvline(mean_val, color='red', linestyle='--', alpha=0.8, 
                      label=f'Média: {mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='--', alpha=0.8, 
                      label=f'Mediana: {median_val:.2f}')
            ax.legend(fontsize=8)
        
        # Remover subplots vazios
        for i in range(len(numeric_cols), n_rows * 2):
            row, col_idx = i // 2, i % 2
            fig.delaxes(axes[row, col_idx])
        
        plt.tight_layout()
        plt.savefig('distribuicoes_numericas.png', dpi=150, bbox_inches='tight')
        print("   ✅ Distribuições salvas: 'distribuicoes_numericas.png'")
        plt.close()
    
    # 2. Boxplots para detecção de outliers
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Normalizar dados para comparação
        df_normalized = df[numeric_cols].copy()
        for col in numeric_cols:
            df_normalized[col] = (df[col] - df[col].mean()) / df[col].std()
        
        df_normalized.boxplot(ax=ax)
        ax.set_title(f'Boxplots Normalizados - {dataset_info["filename"]}')
        ax.set_ylabel('Valores Normalizados (Z-score)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('boxplots_outliers.png', dpi=150, bbox_inches='tight')
        print("   ✅ Boxplots salvos: 'boxplots_outliers.png'")
        plt.close()
    
    # 3. Matriz de correlação
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        correlation_matrix = df[numeric_cols].corr()
        
        # Heatmap
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                   center=0, square=True, fmt='.2f', cbar_kws={"shrink": .8}, ax=ax)
        ax.set_title(f'Matriz de Correlação - {dataset_info["filename"]}')
        plt.tight_layout()
        plt.savefig('matriz_correlacao.png', dpi=150, bbox_inches='tight')
        print("   ✅ Correlações salvas: 'matriz_correlacao.png'")
        plt.close()
        
        # Identificar correlações fortes
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:
                    strong_correlations.append({
                        'Var1': correlation_matrix.columns[i],
                        'Var2': correlation_matrix.columns[j],
                        'Correlação': corr_val
                    })
        
        if strong_correlations:
            print(f"   🔗 Correlações fortes encontradas:")
            for corr in sorted(strong_correlations, key=lambda x: abs(x['Correlação']), reverse=True):
                print(f"      • {corr['Var1']} ↔ {corr['Var2']}: {corr['Correlação']:.3f}")
    
    # 4. Gráficos categóricos
    if len(categorical_cols) > 0:
        n_cat_plots = min(len(categorical_cols), 4)
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        fig.suptitle(f'Variáveis Categóricas - {dataset_info["filename"]}', fontsize=16)
        
        for i, col in enumerate(categorical_cols[:4]):
            ax = axes[i]
            
            # Top 10 valores
            top_values = df[col].value_counts().head(10)
            
            # Gráfico de barras
            top_values.plot(kind='bar', ax=ax, color='lightcoral', alpha=0.8)
            ax.set_title(f'{col} (Top 10)')
            ax.set_xlabel('')
            ax.set_ylabel('Contagem')
            ax.tick_params(axis='x', rotation=45)
            
            # Adicionar valores nas barras
            for j, v in enumerate(top_values.values):
                ax.text(j, v + 0.1, str(v), ha='center', va='bottom', fontsize=8)
        
        # Remover subplots vazios
        for i in range(len(categorical_cols), 4):
            fig.delaxes(axes[i])
        
        plt.tight_layout()
        plt.savefig('variaveis_categoricas.png', dpi=150, bbox_inches='tight')
        print("   ✅ Categóricas salvas: 'variaveis_categoricas.png'")
        plt.close()

def generate_insights(df, dataset_info):
    """Gera insights automáticos baseados na análise"""
    print(f"\n💡 INSIGHTS AUTOMÁTICOS")
    print("=" * 30)
    
    insights = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Insights sobre qualidade dos dados
    missing_pct = (df.isnull().sum().sum() / df.size) * 100
    if missing_pct < 5:
        insights.append("✅ Excelente qualidade dos dados - menos de 5% de valores ausentes")
    elif missing_pct < 15:
        insights.append("⚠️ Qualidade moderada dos dados - alguns valores ausentes para tratar")
    else:
        insights.append("❌ Qualidade baixa dos dados - muitos valores ausentes")
    
    # Insights sobre duplicatas
    dup_pct = (df.duplicated().sum() / len(df)) * 100
    if dup_pct > 10:
        insights.append(f"⚠️ Alto nível de duplicação ({dup_pct:.1f}%) - considere limpeza")
    elif dup_pct > 0:
        insights.append(f"ℹ️ Algumas duplicatas encontradas ({dup_pct:.1f}%)")
    else:
        insights.append("✅ Nenhuma duplicata encontrada")
    
    # Insights sobre variabilidade
    high_var_cols = []
    for col in numeric_cols:
        if df[col].std() / df[col].mean() > 0.5:  # CV > 50%
            high_var_cols.append(col)
    
    if high_var_cols:
        insights.append(f"📈 Variáveis com alta variabilidade: {', '.join(high_var_cols)}")
    
    # Insights específicos para dados de vendas
    if 'valor_total' in df.columns:
        total_vendas = df['valor_total'].sum()
        media_venda = df['valor_total'].mean()
        insights.append(f"💰 Total de vendas: R$ {total_vendas:,.2f}")
        insights.append(f"📊 Ticket médio: R$ {media_venda:,.2f}")
        
        # Top vendedor
        if 'vendedor' in df.columns:
            top_vendedor = df.groupby('vendedor')['valor_total'].sum().idxmax()
            vendas_top = df.groupby('vendedor')['valor_total'].sum().max()
            insights.append(f"🏆 Top vendedor: {top_vendedor} (R$ {vendas_top:,.2f})")
        
        # Forma de pagamento mais comum
        if 'forma_pagamento' in df.columns:
            top_pagamento = df['forma_pagamento'].mode().iloc[0]
            pct_pagamento = (df['forma_pagamento'] == top_pagamento).mean() * 100
            insights.append(f"💳 Forma de pagamento preferida: {top_pagamento} ({pct_pagamento:.1f}%)")
    
    # Imprimir insights
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight}")
    
    return insights

def main():
    """Função principal"""
    print("🐍 ANÁLISE EXPLORATÓRIA AVANÇADA COM PANDAS")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Pandas: {pd.__version__} | NumPy: {np.__version__}")
    
    # Carregar dados
    df, dataset_info = load_data_from_api()
    
    if df is None:
        print("❌ Não foi possível carregar os dados")
        return
    
    # Análise exploratória
    df = perform_exploratory_analysis(df, dataset_info)
    
    # Criar visualizações
    create_visualizations(df, dataset_info)
    
    # Gerar insights
    insights = generate_insights(df, dataset_info)
    
    # Resumo final
    print(f"\n🎉 ANÁLISE CONCLUÍDA!")
    print("=" * 40)
    print(f"📄 Dataset: {dataset_info['filename']}")
    print(f"📐 Dimensões: {df.shape[0]} x {df.shape[1]}")
    print(f"📊 Variáveis numéricas: {len(df.select_dtypes(include=[np.number]).columns)}")
    print(f"🏷️ Variáveis categóricas: {len(df.select_dtypes(include=['object']).columns)}")
    print(f"💾 Memória utilizada: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print(f"📈 Insights gerados: {len(insights)}")
    
    print(f"\n📁 Arquivos gerados:")
    print("   • distribuicoes_numericas.png")
    print("   • boxplots_outliers.png")
    print("   • matriz_correlacao.png")
    print("   • variaveis_categoricas.png")
    
    print(f"\n🚀 Próximos passos recomendados:")
    print("   1. Abrir Jupyter Notebook com kernel 'DataCompass Python'")
    print("   2. Explorar notebook data_exploration.ipynb")
    print("   3. Implementar modelos de Machine Learning")
    print("   4. Criar dashboard interativo")

if __name__ == "__main__":
    main()
