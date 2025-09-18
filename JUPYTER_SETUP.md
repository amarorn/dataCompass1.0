# 📊 Jupyter Notebook - DataCompass

Este guia explica como usar o Jupyter Notebook para análise exploratória avançada dos dados CSV recebidos via WhatsApp.

## 🚀 Início Rápido

### 1. Ativar Ambiente Virtual
```bash
cd /Users/amaro/Documents/amaro/dataCompass1.0
source venv_datacompass/bin/activate
```

### 2. Iniciar Jupyter Notebook
```bash
jupyter notebook
```

### 3. Abrir o Notebook
- No navegador que abrir, navegue até `data_exploration.ipynb`
- Selecione o kernel **"DataCompass Python"** no menu Kernel > Change Kernel

## 📋 Estrutura do Notebook

O notebook `data_exploration.ipynb` contém:

1. **Configuração Inicial**
   - Instalação de dependências
   - Importação de bibliotecas
   - Configurações de visualização

2. **Conexão com Dados**
   - Conexão MongoDB
   - Acesso à API do WhatsApp
   - Carregamento de datasets

3. **Análise Exploratória**
   - Estatísticas descritivas
   - Análise de qualidade dos dados
   - Detecção de outliers e anomalias

4. **Visualizações Interativas**
   - Gráficos com matplotlib e seaborn
   - Plots interativos com plotly
   - Dashboards customizáveis

5. **Machine Learning Exploratório**
   - Preparação de dados
   - Clustering e PCA
   - Modelos preditivos básicos

## 🛠️ Bibliotecas Disponíveis

### Análise de Dados
- **pandas**: Manipulação e análise de dados
- **numpy**: Computação numérica
- **scipy**: Estatísticas avançadas

### Visualização
- **matplotlib**: Gráficos estáticos
- **seaborn**: Visualizações estatísticas
- **plotly**: Gráficos interativos

### Machine Learning
- **scikit-learn**: Algoritmos de ML
- **sklearn**: Pré-processamento e métricas

### Conexão de Dados
- **pymongo**: Acesso ao MongoDB
- **requests**: Chamadas à API

## 📊 Exemplos de Uso

### Carregar Dados
```python
# Buscar datasets disponíveis
raw_data_response = get_raw_data_from_api()
datasets = raw_data_response['data']

# Carregar dataset específico
message_id = datasets[0]['messageId']
df, dataset_info = load_dataset_by_message_id(message_id)
```

### Análise Básica
```python
# Informações gerais
print(f"Dimensões: {df.shape}")
print(f"Colunas: {list(df.columns)}")
print(f"Tipos: {df.dtypes}")

# Estatísticas descritivas
df.describe()
```

### Visualizações
```python
# Distribuições
df.hist(figsize=(15, 10))
plt.tight_layout()
plt.show()

# Correlações
import seaborn as sns
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
plt.show()

# Boxplots para outliers
df.boxplot(figsize=(12, 8))
plt.show()
```

### Análise Categórica
```python
# Contagem de valores
for col in df.select_dtypes(include=['object']).columns:
    print(f"\n{col}:")
    print(df[col].value_counts().head())
    
# Gráficos de barras
categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols:
    plt.figure(figsize=(10, 6))
    df[col].value_counts().head(10).plot(kind='bar')
    plt.title(f'Distribuição: {col}')
    plt.xticks(rotation=45)
    plt.show()
```

## 🔍 Análise Específica para Dados de Vendas

### KPIs Principais
```python
# Total de vendas
total_vendas = df['valor_total'].sum()
print(f"Total de vendas: R$ {total_vendas:,.2f}")

# Ticket médio
ticket_medio = df['valor_total'].mean()
print(f"Ticket médio: R$ {ticket_medio:,.2f}")

# Top produtos
top_produtos = df.groupby('produto_id')['valor_total'].sum().sort_values(ascending=False)
print("Top produtos por valor:")
print(top_produtos.head())
```

### Análise por Vendedor
```python
# Performance por vendedor
vendedor_stats = df.groupby('vendedor').agg({
    'valor_total': ['sum', 'mean', 'count'],
    'quantidade': 'sum'
}).round(2)

print(vendedor_stats.sort_values(('valor_total', 'sum'), ascending=False))
```

### Análise Temporal
```python
# Converter data se necessário
df['data_venda'] = pd.to_datetime(df['data_venda'])

# Vendas por dia da semana
vendas_por_dia = df.groupby(df['data_venda'].dt.day_name())['valor_total'].sum()
vendas_por_dia.plot(kind='bar', figsize=(10, 6))
plt.title('Vendas por Dia da Semana')
plt.show()
```

## 🤖 Machine Learning Básico

### Preparação dos Dados
```python
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Separar variáveis numéricas e categóricas
numeric_cols = df.select_dtypes(include=[np.number]).columns
categorical_cols = df.select_dtypes(include=['object']).columns

# Normalizar dados numéricos
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[numeric_cols] = scaler.fit_transform(df[numeric_cols])
```

### Clustering
```python
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# PCA para visualização
pca = PCA(n_components=2)
df_pca = pca.fit_transform(df[numeric_cols])

# K-means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(df[numeric_cols])

# Visualizar clusters
plt.figure(figsize=(10, 8))
plt.scatter(df_pca[:, 0], df_pca[:, 1], c=clusters, cmap='viridis')
plt.title('Clusters de Vendas (PCA)')
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} da variância)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} da variância)')
plt.colorbar()
plt.show()
```

### Detecção de Anomalias
```python
from sklearn.ensemble import IsolationForest

# Isolation Forest
iso_forest = IsolationForest(contamination=0.1, random_state=42)
anomalies = iso_forest.fit_predict(df[numeric_cols])

# Visualizar anomalias
df['anomalia'] = anomalies == -1
print(f"Anomalias detectadas: {df['anomalia'].sum()}")

# Mostrar registros anômalos
print("\nRegistros anômalos:")
print(df[df['anomalia']][['venda_id', 'valor_total', 'quantidade']])
```

## 📈 Visualizações Interativas com Plotly

### Gráfico de Dispersão Interativo
```python
import plotly.express as px

fig = px.scatter(df, x='quantidade', y='valor_total', 
                 color='forma_pagamento', size='valor_unitario',
                 hover_data=['vendedor', 'produto_id'],
                 title='Relação Quantidade vs Valor Total')
fig.show()
```

### Gráfico de Barras Interativo
```python
# Vendas por forma de pagamento
pagamento_stats = df.groupby('forma_pagamento')['valor_total'].sum().reset_index()

fig = px.bar(pagamento_stats, x='forma_pagamento', y='valor_total',
             title='Vendas por Forma de Pagamento',
             color='valor_total')
fig.show()
```

## 🔧 Dicas e Truques

### 1. Salvar Análises
```python
# Salvar DataFrame processado
df.to_csv('dados_processados.csv', index=False)

# Salvar gráficos
plt.savefig('minha_analise.png', dpi=300, bbox_inches='tight')
```

### 2. Funções Utilitárias
```python
def analise_rapida(df):
    """Análise rápida de qualquer DataFrame"""
    print(f"📊 Dimensões: {df.shape}")
    print(f"📋 Colunas: {list(df.columns)}")
    print(f"❓ Valores ausentes: {df.isnull().sum().sum()}")
    print(f"🔄 Duplicatas: {df.duplicated().sum()}")
    print(f"💾 Memória: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    return df.describe()

# Usar a função
analise_rapida(df)
```

### 3. Exportar para Excel
```python
# Múltiplas abas
with pd.ExcelWriter('analise_completa.xlsx') as writer:
    df.to_excel(writer, sheet_name='Dados_Originais', index=False)
    df.describe().to_excel(writer, sheet_name='Estatisticas')
    df.corr().to_excel(writer, sheet_name='Correlacoes')
```

## 🚨 Solução de Problemas

### Kernel não encontrado
```bash
# Reinstalar kernel
source venv_datacompass/bin/activate
python -m ipykernel install --user --name=datacompass_env --display-name="DataCompass Python"
```

### Bibliotecas não encontradas
```bash
# Reinstalar dependências
source venv_datacompass/bin/activate
pip install pandas numpy matplotlib seaborn plotly scipy scikit-learn pymongo requests
```

### Servidor não responde
```bash
# Verificar se API está rodando
curl http://localhost:3000/api/whatsapp/raw

# Se não estiver, iniciar:
npm start
```

## 📚 Recursos Adicionais

- [Documentação Pandas](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Plotly Documentation](https://plotly.com/python/)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

## ✅ Checklist de Uso

- [ ] Ambiente virtual ativado
- [ ] Jupyter Notebook iniciado
- [ ] Kernel "DataCompass Python" selecionado
- [ ] API do WhatsApp rodando (porta 3000)
- [ ] MongoDB conectado
- [ ] Dados carregados no notebook

---

🎉 **Pronto!** Agora você pode fazer análises exploratórias avançadas dos seus dados CSV usando Python e Jupyter Notebook!
