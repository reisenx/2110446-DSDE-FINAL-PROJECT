# streamlit_app.py

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# PAGE

st.set_page_config(
    page_title='Thailand Election Analytics',
    layout='wide'
)

st.title('Thailand Election Analytics Dashboard')

st.markdown("""
Interactive dashboard for analyzing:
- Election anomalies
- Political support patterns
- PCA vote clustering
""")

# LOAD DATA

@st.cache_data
def load_data():
    return pd.read_csv('cleaned_election_data.csv')

try:
    data = load_data()

except:
    st.error(
        'Please place cleaned_election_data.csv in the same folder.'
    )
    st.stop()

# CLEANING

data['score'] = pd.to_numeric(
    data['score'],
    errors='coerce'
)

data['polling_unit'] = pd.to_numeric(
    data['polling_unit'],
    errors='coerce'
)

data = data.dropna(subset=['score'])

# SIDEBAR

st.sidebar.header('Dashboard Filters')

districts = sorted(
    data['district'].astype(str).unique()
)

parties = sorted(
    data['party_clean'].astype(str).unique()
)

selected_districts = st.sidebar.multiselect(
    'District',
    districts,
    default=districts
)

selected_parties = st.sidebar.multiselect(
    'Party',
    parties,
    default=parties
)

anomaly_filter = st.sidebar.selectbox(
    'Anomaly',
    ['All', 'Only Normal', 'Only Anomaly']
)

# FILTER DATA

filtered_data = data[
    data['district'].isin(selected_districts)
]

filtered_data = filtered_data[
    filtered_data['party_clean'].isin(selected_parties)
]

if anomaly_filter == 'Only Normal':
    filtered_data = filtered_data[
        filtered_data['anomaly'] == 0
    ]

elif anomaly_filter == 'Only Anomaly':
    filtered_data = filtered_data[
        filtered_data['anomaly'] == 1
    ]

# OVERVIEW

st.subheader('Dataset Overview')

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    'Records',
    len(filtered_data)
)

c2.metric(
    'Districts',
    filtered_data['district'].nunique()
)

c3.metric(
    'Parties',
    filtered_data['party_clean'].nunique()
)

c4.metric(
    'Anomalies',
    int(filtered_data['anomaly'].sum())
)

# TABS

tab1, tab2, tab3, tab4 = st.tabs([
    'Anomaly Detection',
    'Political Heatmap',
    'PCA Clustering',
    'Raw Dataset'
])

# ANOMALY DETECTION

with tab1:

    st.subheader('Election Anomaly Detection')

    top_districts = (
        filtered_data['district']
        .value_counts()
        .head(15)
        .index
    )

    plot_data = filtered_data[
        filtered_data['district'].isin(top_districts)
    ]

    fig = px.scatter(
        plot_data,
        x='district',
        y='score',
        color='anomaly',
        hover_data=[
            'party_clean',
            'polling_unit',
            'subdistrict'
        ],
        title='Detected Voting Anomalies'
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    anomaly_rows = filtered_data[
        filtered_data['anomaly'] == 1
    ]

    st.markdown(f"""
### Insight
- Total detected anomalies: **{len(anomaly_rows)}**
- Outlier voting patterns may indicate:
    - OCR errors
    - unusual voting concentration
    - inconsistent polling behavior
""")

    st.dataframe(
        anomaly_rows[
            [
                'district',
                'subdistrict',
                'polling_unit',
                'party_clean',
                'score'
            ]
        ].head(20)
    )

# HEATMAP

with tab2:

    st.subheader('Political Support Heatmap')

    heatmap_data = filtered_data.pivot_table(
        values='score',
        index='district',
        columns='party_clean',
        aggfunc='mean'
    )

    fig, ax = plt.subplots(figsize=(14,8))

    sns.heatmap(
        heatmap_data,
        cmap='RdYlBu_r',
        ax=ax
    )

    ax.set_title(
        'Average Political Support by District'
    )

    st.pyplot(fig)

    st.markdown("""
### Insight
- Strong color intensity indicates concentrated support.
- Different districts show distinct political preferences.
- Heatmaps reveal regional political strongholds.
""")

# PCA

with tab3:

    st.subheader('PCA Voting Pattern Clustering')

    try:

        pca_features = filtered_data[[
            'score',
            'party_encoded',
            'district_encoded',
            'subdistrict_encoded',
            'polling_unit'
        ]].copy()

        pca_features = pca_features.apply(
            pd.to_numeric,
            errors='coerce'
        )

        valid_index = pca_features.dropna().index

        pca_features = pca_features.loc[valid_index]

        pca_data = filtered_data.loc[valid_index].copy()

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(
            pca_features
        )

        pca = PCA(n_components=2)

        X_pca = pca.fit_transform(X_scaled)

        pca_data['PCA1'] = X_pca[:,0]
        pca_data['PCA2'] = X_pca[:,1]

        fig = px.scatter(
            pca_data,
            x='PCA1',
            y='PCA2',
            color='party_clean',
            symbol='anomaly',
            hover_data=[
                'district',
                'subdistrict',
                'score'
            ],
            title='Voting Pattern Clustering'
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        variance = round(
            pca.explained_variance_ratio_.sum() * 100,
            2
        )

        st.markdown(f"""
### PCA Insight
- Explained variance: **{variance}%**
- Nearby points represent similar voting behavior.
- Outlier clusters may indicate unusual election patterns.
""")

    except Exception as e:

        st.error('PCA visualization failed.')
        st.write(e)

# RAW DATA

with tab4:

    st.subheader('Filtered Dataset')

    st.dataframe(filtered_data)

    csv = filtered_data.to_csv(
        index=False
    ).encode('utf-8')

    st.download_button(
        'Download Filtered Dataset',
        csv,
        'filtered_election_data.csv',
        'text/csv'
    )

# FOOTER

st.markdown('---')

st.markdown("""
Thailand Election Analytics Project

Techniques:
- Isolation Forest
- PCA
- Heatmap Analytics
- Election Pattern Mining
- Noisy Data Cleaning
""")