import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
import json

st.set_page_config(
    page_title="Japan GIS Risk Analysis",
    page_icon="🇯🇵",
    layout="wide"  
)


st.title("🇯🇵 Japan Disaster Risk Analysis")
st.write(
    """
    This website showcases the 'Population Density' and the 'Holistic Risk Score' for all 47 Japanese prefectures, 
    combining data on floods, landslides, and human vulnerability. Based off of Data from the Statistics Bureau of Japan and the official census of Japan.
    """
)


@st.cache_data
def load_data():
    flood_df = pd.read_excel('flood.xlsx',header=7)
    flood_df.rename(columns={'死者，\n行方不明者': 'killed_or_missing', '負傷者': 'injured', '全壊':'ruined','半壊':'half_ruined','床上\n浸水':'flood_above_floor', '床下\n浸水':'flood_below_floor','河川\n（箇所）':'rivers','崖くずれ（箇所）':'landslides','House-holds \naffected':'households_affected','Persons affected':'persons_affected','Prefecture':'join_key'}, 
                inplace=True)
    flood_df = flood_df.drop(flood_df.columns[[0]],axis=1)
    flood_df = flood_df.dropna().reset_index(drop=True)

    flood_df = flood_df.rename(columns={'Prefecture': 'join_key'})

    population_df = pd.read_csv('Japan_population_data.csv')
    population_df = population_df.drop(population_df.columns[[3,4]],axis=1)
    mask = (population_df['year'] > 2015)
    population_df = population_df[mask]
    population_df['prefecture'] = population_df['prefecture'].str.replace(r'-(ken|to|fu)$', '', regex=True)
    population_df = population_df.rename(columns={'prefecture': 'join_key'})
    population_df = population_df.reset_index(drop=True)

    final_gdf = population_df.merge(flood_df, on='join_key', how='left')
    mask_1 = ['households_affected','persons_affected','killed_or_missing','injured','ruined','half_ruined','flood_above_floor','flood_below_floor','rivers','landslides']
    final_gdf[mask_1] = final_gdf[mask_1].apply(pd.to_numeric, errors='coerce')
    final_gdf[mask_1] = final_gdf[mask_1].fillna(0)

    final_gdf['total_floods'] = final_gdf['flood_above_floor'] + final_gdf['flood_below_floor']
    final_gdf['total_floods_per_km2'] = final_gdf['total_floods'] / final_gdf['estimated_area']
    final_gdf['landslides_per_km2'] = final_gdf['landslides'] / final_gdf['estimated_area']
    final_gdf['houses_ruined_per_km2'] = final_gdf['ruined']/final_gdf['estimated_area']
    final_gdf['houses_half_ruined_per_km2'] = final_gdf['half_ruined']/final_gdf['estimated_area']

    final_gdf['persons_affected_per_100k_people'] = (final_gdf['persons_affected'] / final_gdf['population']) * 100000
    final_gdf['killed_or_missing_per_100k_people'] = (final_gdf['killed_or_missing'] / final_gdf['population']) * 100000
    final_gdf['injured_per_100k_people'] = (final_gdf['injured'] / final_gdf['population']) * 100000

    final_gdf = final_gdf.rename(columns={'join_key': 'prefecture'})
    final_gdf = final_gdf.sort_values(by='population', ascending=False).reset_index(drop=True)

    risk_columns = ['total_floods_per_km2','landslides_per_km2','houses_ruined_per_km2','houses_half_ruined_per_km2','persons_affected_per_100k_people','killed_or_missing_per_100k_people','injured_per_100k_people']

    scaler = MinMaxScaler()
    final_gdf[risk_columns] = scaler.fit_transform(final_gdf[risk_columns])
    final_gdf['holistic_risk_score'] = (final_gdf[risk_columns].sum(axis=1))+1
    final_gdf = final_gdf.drop(['island', 'rivers'], axis=1)
    final_gdf = final_gdf.rename(columns={'persons_affected':'people_affected','ruined':'houses_ruined','half_ruined':'houses_half_ruined'})

    top_five_df = final_gdf.sort_values(by=['holistic_risk_score'], ascending=False).head().reset_index(drop=True)
    mask_top_five = ['prefecture','holistic_risk_score']
    top_five_df = top_five_df[mask_top_five]

    top_five_pop_df = final_gdf.sort_values(by=['population'], ascending=False).head().reset_index(drop=True)
    mask_top_pop_five = ['prefecture','population']
    top_five_pop_df = top_five_pop_df[mask_top_pop_five]

    with open('japan_prefectures.geojson', 'r', encoding='utf-8') as f:
        japan_geojson = json.load(f)

        fig = px.choropleth_map(
        final_gdf, 
        geojson=japan_geojson,  
        locations='prefecture',  
        featureidkey='id', 
        color='population',  
        color_continuous_scale="Viridis",
        range_color=(0, final_gdf['population'].max()),
        map_style="carto-positron",
        zoom=3.8,
        center={"lat": 36, "lon": 138},
        opacity=0.6,
        hover_name='prefecture',
        hover_data={
            'population': ':,',
            'people_affected': ':,',
            'killed_or_missing': ':,',
            'injured': ':,'
        },
        labels={
            'population': 'Population (2015)',
            'people_affected': 'People Affected',
            'killed_or_missing': 'Killed/Missing'
        }
    )

    fig.update_layout(
        title='Figure 3: Japan Prefecture Population and Disaster Impact per Prefecture',
        height=800,
        width=1200 
    )

    fig_3 = px.choropleth_map(
        final_gdf, 
        geojson=japan_geojson,  
        locations='prefecture',  
        featureidkey='id', 
        color='holistic_risk_score',  
        color_continuous_scale='thermal',
        range_color=(1, final_gdf['holistic_risk_score'].max()),
        map_style="carto-positron",
        zoom=3.8,
        center={"lat": 36, "lon": 138},
        opacity=0.6,
        hover_name='prefecture',
        hover_data={
            'holistic_risk_score': ':,',
            'people_affected': ':,',
            'killed_or_missing': ':,',
            'injured': ':,',
            'households_affected': ':,'
            
        },
        labels={
            'holistic_risk_score': 'Holistic Risk Score',
            'persons_affected': 'People Affected',
            'killed_or_missing': 'Killed/Missing'
        }
    )

    fig_3.update_layout(
        title='Figure 2: Holistic Disaster Risk Index for Japan',
        height=800,
        width=1200 
    )    
    
    return fig, fig_3, final_gdf, top_five_df, top_five_pop_df

fig, fig_3, final_gdf, top_five_df, top_five_pop_df = load_data()

st.sidebar.header("Figure 1 Controls")
mappable_features = [
    'total_floods',
    'injured',
    'houses_ruined',
    'houses_half_ruined',
    'landslides'
]
selected_feature = st.sidebar.selectbox(
    "Select a risk feature to apply to figure 1:",
    mappable_features
)
with open('japan_prefectures.geojson', 'r', encoding='utf-8') as f:
        japan_geojson = json.load(f)

fig_2 = px.choropleth_map(
        final_gdf, 
        geojson=japan_geojson,  
        locations='prefecture',  
        featureidkey='id', 
        color=selected_feature,  
        color_continuous_scale='Sunset',
        range_color=(0, final_gdf[selected_feature].max()),
        map_style="carto-positron",
        zoom=3.8,
        center={"lat": 36, "lon": 138},
        opacity=0.6,
        hover_name='prefecture',
        hover_data={
            selected_feature : ':,',
            'people_affected': ':,',
            'households_affected': ':,'
        },
        labels={
            selected_feature: selected_feature,
            'persons_affected': 'People Affected',
            'households_affected': 'Households Affected'
        }
    )

fig_2.update_layout(
        title='Figure 1: Map colored by selected column',
        height=800,
        width=1200 
    )

st.header(f"Map displaying {selected_feature}")
st.plotly_chart(fig_2, use_container_width=True)

st.header("Holistic Risk Score Map")
st.plotly_chart(fig_3, use_container_width=True)

st.header("Population Density Map")
st.plotly_chart(fig, use_container_width=True)

st.sidebar.header("Top 5 Prefectures At Risk")
st.sidebar.dataframe(top_five_df)

st.sidebar.header("Top 5 Most Populated Prefectures")
st.sidebar.dataframe(top_five_pop_df)

st.header("Cleaned Data")
st.write("The Cleaned Data Frame Used for the Analysis.")
st.dataframe(final_gdf)

st.header("Sources")
st.write("2015 Japanese Prefecture Population and Area Source: https://www.kaggle.com/datasets/jd1325/japan-population-data")
st.write("2019 Natural Disasters Source: https://www.stat.go.jp/english/data/nenkan/68nenkan/1431-29.html")
st.write("Kaggle GeoJSON Source: https://www.kaggle.com/datasets/zhanhaoh/geographic-data-of-japan")