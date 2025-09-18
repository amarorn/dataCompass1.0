#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para análise exploratória dos dados CSV recebidos via WhatsApp
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from pymongo import MongoClient
import warnings
from datetime import datetime

# Configurações
warnings.filterwarnings('ignore')
plt.style.use('default')
sns.set_palette("husl")

def test_mongodb_connection():
    """Testa conexão com MongoDB"""
    try:
        client = MongoClient("mongodb://localhost:27017/datacompass")
        db = client.datacompass
        
        # Testar ping
        db.admin.command('ping')
        print("✅ Conexão MongoDB bem-sucedida")
        
        # Listar coleções
        collections = db.list_collection_names()
        print(f"📂 Coleções disponíveis: {collections}")
        
        # Contar documentos em cada coleção
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"   • {collection}: {count} documentos")
        
        return db
    except Exception as e:
        print(f"❌ Erro ao conectar ao MongoDB: {e}")
        return None

def test_api_connection():
    """Testa conexão com a API"""
    try:
        response = requests.get("http://localhost:3000/api/whatsapp/raw")
        if response.status_code == 200:
            data = response.json()
            print("✅ Conexão API bem-sucedida")
            
            if data.get('success') and data.get('data'):
                datasets = data['data']
                print(f"📊 Encontrados {len(datasets)} datasets via API")
                
                for i, dataset in enumerate(datasets):
                    print(f"   {i+1}. {dataset['filename']} - {dataset['recordCount']} registros")
                
                return datasets
            else:
                print("⚠️ API respondeu mas sem dados")
                return []
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao conectar à API: {e}")
        return None

def load_and_analyze_data():
    """Carrega e analisa dados disponíveis"""
    print("\n🔍 CARREGANDO E ANALISANDO DADOS")
    print("=" * 40)
    
    # Testar conexões
    db = test_mongodb_connection()
    datasets = test_api_connection()
    
    if not datasets:
        print("❌ Nenhum dataset disponível para análise")
        return
    
    # Carregar o primeiro dataset
    dataset = datasets[0]
    message_id = dataset['messageId']
    
    print(f"\n📊 Analisando dataset: {dataset['filename']}")
    print(f"🆔 Message ID: {message_id[:30]}...")
    
    try:
        # Buscar dados via API
        response = requests.get(f"http://localhost:3000/api/whatsapp/raw/{message_id}")
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                # Criar DataFrame
                df = pd.DataFrame(data['data']['rawData'])
                
                print(f"✅ DataFrame criado: {df.shape[0]} linhas x {df.shape[1]} colunas")
                print(f"📋 Colunas: {list(df.columns)}")
                
                # Análise básica
                print("\n📈 ANÁLISE EXPLORATÓRIA BÁSICA")
                print("-" * 35)
                
                print("🔍 Informações gerais:")
                print(f"   • Dimensões: {df.shape}")
                print(f"   • Tipos de dados: {df.dtypes.value_counts().to_dict()}")
                print(f"   • Valores ausentes: {df.isnull().sum().sum()}")
                print(f"   • Duplicatas: {df.duplicated().sum()}")
                
                # Primeiras linhas
                print("\n📋 Primeiras 5 linhas:")
                print(df.head())
                
                # Estatísticas descritivas para colunas numéricas
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    print(f"\n📊 Estatísticas numéricas ({len(numeric_cols)} colunas):")
                    print(df[numeric_cols].describe())
                
                # Análise de colunas categóricas
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    print(f"\n🏷️ Colunas categóricas ({len(categorical_cols)} colunas):")
                    for col in categorical_cols[:3]:  # Mostrar apenas as primeiras 3
                        unique_count = df[col].nunique()
                        print(f"   • {col}: {unique_count} valores únicos")
                        if unique_count <= 10:
                            print(f"     - Valores: {df[col].value_counts().head().to_dict()}")
                
                # Criar visualizações simples se possível
                if len(numeric_cols) > 0:
                    print(f"\n📊 Criando visualizações para colunas numéricas...")
                    
                    # Histogramas
                    fig, axes = plt.subplots(min(2, len(numeric_cols)), 2, figsize=(12, 8))
                    if len(numeric_cols) == 1:
                        axes = [axes]
                    elif len(numeric_cols) <= 2:
                        axes = axes.flatten()
                    
                    for i, col in enumerate(numeric_cols[:4]):
                        if len(numeric_cols) == 1:
                            ax = axes[0] if isinstance(axes, list) else axes
                        else:
                            row, col_idx = i // 2, i % 2
                            ax = axes[row, col_idx] if len(numeric_cols) > 2 else axes[i]
                        
                        df[col].hist(bins=20, ax=ax, alpha=0.7, edgecolor='black')
                        ax.set_title(f'Distribuição: {col}')
                        ax.set_xlabel(col)
                        ax.set_ylabel('Frequência')
                    
                    plt.tight_layout()
                    plt.savefig('analise_basica.png', dpi=150, bbox_inches='tight')
                    print("   ✅ Gráficos salvos em 'analise_basica.png'")
                    plt.close()
                
                print(f"\n🎉 ANÁLISE CONCLUÍDA!")
                print("=" * 40)
                print(f"📄 Dataset: {dataset['filename']}")
                print(f"📐 Dimensões: {df.shape[0]} x {df.shape[1]}")
                print(f"📊 Colunas numéricas: {len(numeric_cols)}")
                print(f"🏷️ Colunas categóricas: {len(categorical_cols)}")
                print(f"💾 Dados processados: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                
                return df
                
            else:
                print(f"❌ Erro nos dados da API: {data.get('message')}")
        else:
            print(f"❌ Erro ao buscar dados: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🐍 TESTE DE ANÁLISE EXPLORATÓRIA COM PYTHON")
    print("=" * 50)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    load_and_analyze_data()
    
    print("\n✅ Teste concluído!")
    print("\nPróximos passos:")
    print("1. Abrir Jupyter Notebook")
    print("2. Selecionar kernel 'DataCompass Python'")
    print("3. Executar células do notebook data_exploration.ipynb")
