import streamlit as st
import pandas as pd
import datetime as dt
#import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np

# data preparation
## read data
sheet_id = '1w4sszDjsLmMKZe-_m5VwBojI8l8FdqU5IdAD2iejLuc'
flores_eq = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv')
flores_eq['date'] = pd.to_datetime(flores_eq['date'])
flores_eq['date'] = flores_eq['date'].dt.date
flores_eq.rename(columns={'lat_deg': 'lat', 'long_deg': 'lon'}, inplace=True)

## clustering
flores_latlong = flores_eq[['lat','lon']]
### define
clusterer = KMeans(n_clusters=3)

### fit
clusterer.fit(flores_latlong)

###transform/predict
clusterer.predict(flores_latlong)

flores_latlong['predicted_label'] = clusterer.labels_.astype(int)

fig = plt.figure()
scatter = plt.scatter(flores_latlong['lon'], flores_latlong['lat'], c=clusterer.labels_)
lab_legend=['Cluster 1', 'Cluster 2', 'Cluster 3']
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Segments of Kalaotoa Fault based on clustered eartquakes')
plt.legend(handles=scatter.legend_elements()[0], labels= lab_legend)
#print(flores_eq.head())

#dashboard
st.set_page_config(layout='wide')

st.title('The Kalaotoa Fault: A Newly Identified Fault that Generated the Mw 7.3 Flores Sea Earthquake')

st.header("A damaging earthquake in Indonesia is ascribed to a previously unknown fracture in Earth’s crust.")

met1, met2, met3, met4, = st.columns(4)

with met1:
    st.metric('Magnitude (Mw)', 7.3)
with met2:
    st.metric('Depth (km)', 10)
with met3:
    st.metric('Displaced residents', 5064)
with met4:
    st.metric('Damaged infrastructure', 736)

st.write('There has been an earthquake on Tuesday, December 14, 2021 at 10:20:23 WIB with a magnitude of 7.4. ' +
'The earthquake center (epicenter) is located at coordinates 7.59° South Latitude 122.25° East Longitude is located in the Flores Sea at a depth of 10 km. ' + 
'The earthquake has caused shocks in several areas with an intensity between II to VI on the Mercalli Modified Intensity (MMI) scale. ' +
 'Judging from the source mechanism, this earthquake was triggered by shear fault activity. ' + 
 'Based on sea level observations by BMKG, a tsunami after the M7.4 earthquake has been detected in the Flores Sea.')

st.subheader('Earthquakes Distribution')

col1, col2 = st.columns(2)
with col1:
    def color_mag(val):
        color = 'yellow' if val >= 5.0 else 'white'
        return f'background-color: {color}'
    st.dataframe(
        flores_eq.style.applymap(color_mag, subset=['magnitude']).format({'lat': '{:.3f}', 'lon': '{:.3f}', 'depth_km':'{:.3f}', 'magnitude':'{:.3f}'}), 
        height = 650, 
        use_container_width = True)

with col2:
    start_time = dt.date(2021,12,14)
    end_time = dt.date(2022,3,20)

    select_period = st.slider('Select period:', min_value=start_time, max_value=end_time, value= start_time)

    st.write('Period: ', start_time, 'to ', select_period)

    # Filter data between two dates
    filtered_df = flores_eq.loc[(flores_eq['date'] >= start_time) & (flores_eq['date'] <= select_period)]
    print(filtered_df.tail())

    st.map(filtered_df)

st.subheader('Kalaotoa Fault and Its Three Segments')

col3, col4 = st.columns(2)
with col3:
    st.write('A team led by Pepen Supendi at the University of Cambridge, UK, analysed the depth and locations of the main earthquake, ' +
    'as well as 1,400 aftershocks in the months that followed. The scientists revealed the existence of a newly recognized fault, which they named the Kalaotoa fault.')
    st.write('At least three segments of the fault slipped during the quake, transferring stress to other nearby faults. ' +
     'Understanding this complex geological web is crucial to assessing which parts of Indonesia are most at risk from earthquakes.')

with col4:
    st.pyplot(fig)
