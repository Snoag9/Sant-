import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Santé France", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv('effectifs.csv', sep=';', encoding='utf-8-sig', low_memory=False)
    df_clean = df.dropna(subset=['Ntop', 'Npop', 'prev']).copy()
    return df_clean


df_all = load_data()

st.sidebar.header("🔍 Paramètres")

exclure_liste = [
    'Total consommants tous régimes',
    'Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire',
    'Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité)'
]
toutes_maladies = sorted(df_all['patho_niv1'].unique())
liste_maladies_propre = [m for m in toutes_maladies if m not in exclure_liste]

maladie_choisie = st.sidebar.selectbox("🎯 Choisir une pathologie", liste_maladies_propre)

annees_disponibles = sorted(df_all['annee'].unique(), reverse=True)
annee_choisie = st.sidebar.selectbox("📅 Choisir l'année", annees_disponibles)

st.title(f"📊 Analyse : {maladie_choisie} ({annee_choisie})")

df_filtre = df_all[(df_all['patho_niv1'] == maladie_choisie) & (df_all['annee'] == annee_choisie)]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📈 Prévalence par âge et sexe")
    df_age = df_filtre[
        (df_filtre['libelle_sexe'] != 'tous sexes') & (df_filtre['libelle_classe_age'] != 'tous âges')].copy()

    ordre_age = [
        'de 0 à 4 ans', 'de 5 à 9 ans', 'de 10 à 14 ans', 'de 15 à 19 ans',
        'de 20 à 24 ans', 'de 25 à 29 ans', 'de 30 à 34 ans', 'de 35 à 39 ans',
        'de 40 à 44 ans', 'de 45 à 49 ans', 'de 50 à 54 ans', 'de 55 à 59 ans',
        'de 60 à 64 ans', 'de 65 à 69 ans', 'de 70 à 74 ans', 'de 75 à 79 ans',
        'de 80 à 84 ans', 'de 85 à 89 ans', 'de 90 à 94 ans', 'plus de 95 ans'
    ]
    df_age['libelle_classe_age'] = pd.Categorical(df_age['libelle_classe_age'], categories=ordre_age, ordered=True)
    age_stats = df_age.groupby(['libelle_classe_age', 'libelle_sexe'], observed=True)['prev'].mean().reset_index()

    fig_age = px.line(age_stats, x='libelle_classe_age', y='prev', color='libelle_sexe', markers=True,
                      template="plotly_white")
    st.plotly_chart(fig_age, use_container_width=True)

with col2:
    st.subheader(" Carte de France (Métropole)")
    df_metropole = df_filtre[
        (df_filtre['libelle_sexe'] == 'tous sexes') &
        (df_filtre['libelle_classe_age'] == 'tous âges') &
        (~df_filtre['dept'].astype(str).str.startswith('97')) &
        (~df_filtre['dept'].astype(str).isin(['99', '999', '998']))
        ]

    geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
    fig_map = px.choropleth(df_map := df_metropole, geojson=geojson_url, locations='dept',
                            featureidkey="properties.code",
                            color='prev', color_continuous_scale="OrRd")
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)

st.divider()
st.subheader(" Focus Outre-mer (DROM)")
col_dom = st.columns(5)

noms_dom = {'971': 'Guadeloupe', '972': 'Martinique', '973': 'Guyane', '974': 'La Réunion', '976': 'Mayotte'}

df_dom = df_filtre[
    (df_filtre['libelle_sexe'] == 'tous sexes') &
    (df_filtre['libelle_classe_age'] == 'tous âges') &
    (df_filtre['dept'].astype(str).str.startswith('97'))
    ]

for i, (code, nom) in enumerate(noms_dom.items()):
    valeur = df_dom[df_dom['dept'].astype(str) == code]['prev']
    if not valeur.empty:
        col_dom[i].metric(nom, f"{valeur.values[0]:.2f} %")
    else:
        col_dom[i].metric(nom, "N/A")

st.caption(
    f"Données issues de l'Assurance Maladie (Open Data CNAM). La prévalence correspond au % de la population touchée en {annee_choisie}.")