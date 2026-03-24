import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Chargement des données
df = pd.read_csv(r'Dataset.csv')

print(df.shape)          # (2000, 8)
print(df.dtypes)         # types de chaque colonne
print(df.head())         # aperçu des premières lignes
print(df.isnull().sum()) # valeurs manquantes
print(df.describe())     # statistiques descriptives

# Convertir la date en format datetime
df['TransactionStartTime'] = pd.to_datetime(df['TransactionStartTime'])

# Extraire l'heure et le jour pour l'analyse temporelle
df['Hour'] = df['TransactionStartTime'].dt.hour
df['DayOfWeek'] = df['TransactionStartTime'].dt.day_name()

# Créer une colonne avec la valeur absolue du montant
df['AbsAmount'] = df['Amount'].abs()

# Renommer FraudResult pour plus de clarté
df['IsFraud'] = df['FraudResult'].map({0: 'Légitime', 1: 'Fraude'})

print(df.shape)
df.head()

# Volume de transactions par catégorie
volume_par_categorie = df['ProductCategory'].value_counts().reset_index()
volume_par_categorie.columns = ['Catégorie', 'Nombre']

# Montant moyen par catégorie
montant_moyen = df.groupby('ProductCategory')['AbsAmount'].mean().reset_index()
montant_moyen.columns = ['Catégorie', 'Montant Moyen']

print(volume_par_categorie)
print(montant_moyen)

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(volume_par_categorie['Catégorie'], volume_par_categorie['Nombre'], color='steelblue')
ax.set_title('Nombre de transactions par catégorie de produit')
ax.set_xlabel('Catégorie')
ax.set_ylabel('Nombre de transactions')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 5))
sns.boxplot(data=df, x='ProductCategory', y='AbsAmount', palette='Set2')
plt.title('Distribution des montants par catégorie')
plt.xlabel('Catégorie')
plt.ylabel('Montant (valeur absolue)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 4))
sns.countplot(data=df, x='Hour', palette='Blues_d')
plt.title('Nombre de transactions par heure de la journée')
plt.xlabel('Heure')
plt.ylabel('Nombre de transactions')
plt.tight_layout()
plt.show()

fig = px.bar(
    montant_moyen,
    x='Catégorie',
    y='Montant Moyen',
    color='Catégorie',
    title='Montant moyen des transactions par catégorie',
    text_auto='.0f'
)
fig.update_layout(showlegend=False)
fig.show()

canal_counts = df['ChannelId'].value_counts().reset_index()
canal_counts.columns = ['Canal', 'Nombre']

fig2 = px.pie(
    canal_counts,
    names='Canal',
    values='Nombre',
    title='Répartition des transactions par canal'
)
fig2.show()

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Dashboard Transactions", layout="wide")
st.title("Dashboard — Analyse des Transactions")

# --- Chargement des données ---
@st.cache_data
def load_data():
    df = pd.read_csv(r'Dataset.csv')
    df['TransactionStartTime'] = pd.to_datetime(df['TransactionStartTime'])
    df['Hour'] = df['TransactionStartTime'].dt.hour
    df['AbsAmount'] = df['Amount'].abs()
    return df

df = load_data()

# --- Filtres dans la barre latérale ---
st.sidebar.header("🔧 Filtres")
categories = st.sidebar.multiselect(
    "Catégories de produits",
    options=df['ProductCategory'].unique(),
    default=df['ProductCategory'].unique()
)

canaux = st.sidebar.multiselect(
    "Canaux",
    options=df['ChannelId'].unique(),
    default=df['ChannelId'].unique()
)

# --- Filtrage du dataframe ---
df_filtre = df[
    df['ProductCategory'].isin(categories) &
    df['ChannelId'].isin(canaux)
]

# --- KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Total transactions", len(df_filtre))
col2.metric("Montant moyen", f"{df_filtre['AbsAmount'].mean():,.0f}")
col3.metric("Cas de fraude", df_filtre['FraudResult'].sum())

st.markdown("---")

# --- Graphiques ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Transactions par catégorie")
    fig1 = px.bar(
        df_filtre['ProductCategory'].value_counts().reset_index(),
        x='ProductCategory', y='count',
        color='ProductCategory', labels={'count': 'Nombre'}
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Répartition par canal")
    fig2 = px.pie(
        df_filtre, names='ChannelId',
        title='Part de chaque canal'
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Montant moyen par catégorie")
fig3 = px.bar(
    df_filtre.groupby('ProductCategory')['AbsAmount'].mean().reset_index(),
    x='ProductCategory', y='AbsAmount',
    labels={'AbsAmount': 'Montant moyen'}, color='ProductCategory'
)
st.plotly_chart(fig3, use_container_width=True)
