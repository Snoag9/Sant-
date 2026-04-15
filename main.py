import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


print("Chargement des données...")
df = pd.read_csv('effectifs.csv', sep=';', encoding='utf-8-sig', low_memory=False)
df_clean = df.dropna(subset=['Ntop', 'Npop', 'prev']).copy()

df_dept = df_clean[~df_clean['dept'].astype(str).isin(['99', '999', '998'])].copy()
derniere_annee = df_dept['annee'].max()
df_final = df_dept[df_dept['annee'] == derniere_annee]


print("Génération du Pie Chart...")

exclure = ['Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire',
           'Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité)']
df_pie = df_final[(df_final['libelle_sexe'] == 'tous sexes') &
                  (df_final['libelle_classe_age'] == 'tous âges') &
                  (~df_final['patho_niv1'].isin(exclure))]

top_10 = df_pie.groupby('patho_niv1')['Ntop'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 10))
plt.pie(top_10, labels=top_10.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
plt.title(f'Répartition du Top 10 des Pathologies (Patients en {derniere_annee})')
plt.tight_layout()
plt.show(block=False)

print("Génération de la carte interactive (devrait s'ouvrir dans le navigateur)...")
df_map = df_final[(df_final['patho_niv1'] == 'Diabète') &
                  (df_final['libelle_sexe'] == 'tous sexes') &
                  (df_final['libelle_classe_age'] == 'tous âges')]

geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"

fig = px.choropleth(
    df_map, geojson=geojson_url, locations='dept', featureidkey="properties.code",
    color='prev', color_continuous_scale="OrRd", title=f"Prévalence du Diabète par département ({derniere_annee})"
)
fig.update_geos(fitbounds="locations", visible=False)
fig.show()

plt.show()