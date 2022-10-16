import streamlit as st
import pandas as pd
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib.dates import DateFormatter
from scipy import stats
import matplotlib.dates as mdates
from PIL import Image


# data preparation
## read data
sheet_id = '1w4sszDjsLmMKZe-_m5VwBojI8l8FdqU5IdAD2iejLuc'
flores_eq = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv')
flores_eq['date'] = pd.to_datetime(flores_eq['date'], format='%d/%m/%Y')
flores_eq['date'] = flores_eq['date'].dt.date
flores_eq.rename(columns={'lat_deg': 'lat', 'long_deg': 'lon'}, inplace=True)

## plotting date vs magnitude
fig1, ax = plt.subplots(figsize=(12, 8))
ax.stem(flores_eq['date'], flores_eq['magnitude'], linefmt='black')
ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
ax.xaxis.set_major_locator(mdates.DayLocator(14))
plt.xlabel('Date')
plt.ylabel('Magnitude')
ax.annotate('Mainshock', (datetime.strptime('2021-12-14','%Y-%m-%d'),7.4), size=16)
ax.plot([datetime.strptime('2021-12-14','%Y-%m-%d'), datetime.strptime('2022-03-20','%Y-%m-%d')],[6.0,6.0],
       color='green', linestyle='--')
ax.annotate('Aftershock', (datetime.strptime('2022-01-25','%Y-%m-%d'),6.1), size=16)
plt.show()

## clustering
flores_latlong = flores_eq[['lat','lon']]
### define
clusterer = KMeans(n_clusters=3)

### fit
clusterer.fit(flores_latlong)

###transform/predict
clusterer.predict(flores_latlong)
flores_latlong['predicted_label'] = clusterer.labels_.astype(int)
cluster = flores_latlong['predicted_label'].unique()

# plotting clustered data & segment line
## regression function
def CreateLine(x, intercept, slope):
  return slope * x + intercept

## colors for clustered and segment
colors = ['gold','indigo','teal']
segs_colors = ['blue','green','brown']

## plotting figure
fig2 = plt.figure(figsize=[12,8])

### basemap
m = Basemap(resolution='i',
            llcrnrlat=-9.2,urcrnrlat=-6.0,llcrnrlon=119.5,urcrnrlon=123.5)
m.shadedrelief()
plt.yticks(np.arange(-9.2, -6.0, step=1))
plt.xticks(np.arange(119.5, 123.5, step=1))

### scatter and segment
for i in np.sort(np.unique(clusterer.labels_)):
    filtered = flores_latlong[flores_latlong['predicted_label']==i]
    filtered_long = filtered['lon']
    filtered_lat = filtered['lat']
    
    slope, intercept, r, p, std_err = stats.linregress(filtered_long, filtered_lat)
    
    scatter = plt.scatter(filtered_long, filtered_lat, c=colors[i],label='Cluster ' + str(i + 1))
    
    regression_line = [CreateLine(i, intercept, slope) for i in filtered_long]
    plt.plot(filtered_long, regression_line, c = segs_colors[i], label='Segment ' + str(i + 1), linewidth=4)
    
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Segments of Kalaotoa Fault based on clustered eartquakes')
plt.legend()
plt.show()

#scatter = plt.scatter(flores_latlong['lon'], flores_latlong['lat'], c=clusterer.labels_)
#lab_legend=['Cluster ' + str(cluster[0]+1) , 'Cluster ' + str(cluster[1]+1), 'Cluster ' + str(cluster[2]+1)]
#lab_legend=['Cluster 1', 'Cluster 2', 'Cluster 3']
#plt.legend(handles=scatter.legend_elements()[0], labels= lab_legend)
#print(scatter.legend_elements())

#dashboardss
st.set_page_config(layout='wide')

st.title('Sesar Kalaotoa: Sesar Baru yang Menyebabkan Terjadinya Gempa Bermagnitudo 7.3 di Laut Flores')

st.header("Gempa merusak di Indonesia disebabkan oleh sesar yang sebelumnya tidak teridentifikasi di kerak bumi.")
met1, met2, met3, met4, = st.columns(4)

with met1:
    st.metric('Magnitudo (Mw)', 7.3)
with met2:
    st.metric('Kedalaman (km)', 10)
with met3:
    st.metric('Jumlah korban yang harus mengungsi', 5064)
with met4:
    st.metric('Jumlah infrastruktur yang rusak', 736)

col11, col12 = st.columns(2)
with col11:
    image = Image.open('warga_mengungsi.jpeg')
    st.image(image, caption='Warga Pulau Selayar yang mengungsi akibat gempa 14 Desember 2021')

with col12:

    st.write('Telah terjadi gempa pada hari Selasa, 14 Desember 2021 pukul 10:20:23 WIB dengan magnitudo 7.3. Pusat gempa terletak di Laut Flores ' +
    'pada koordinat 7.59°LS dan 122.24°BT dengan magnitudo 7.3 pada kedalaman 10 km dan berjarak sekitar 115 km utara Kota Maumere (ibu kota Kabupaten Sikka), ' +
    'Provinsi Nusa Tenggara Timur, atau berjarak sekitar 256.6 km tenggara Kota Benteng (ibu kota Kabupaten Kepulauan Selayar), Provinsi Sulawesi Selatan. ' +
    'Dilihat dari mekanisme sumbernya, gempa ini dipicu oleh aktivitas Sesar Kalaotoa, sebuah sesar geser yang sebelumnya tidak diketahui keberadaannya. ' +
    'Menurut data Badan Informasi Geospasial (BIG) kejadian gempa tersebut memicu ' +
    'terjadinya tsunami kecil setinggi 7 cm yang teramati di pantai Marapokot, Kabupaten Nagekeo, Provinsi Nusa Tenggara Timur. ')

st.write('Pulau Selayar dan Pulau Flores merupakan dua pulau yang terkena dampak dari gempa ini. ' + 
    'Guncangan maksimum terjadi di Kecamatan Pasilambena, Kabupaten Kepulauan Selayar dan mencapai skala intensitas VII MMI. ' + 
    'Menurut Badan Nasional Penanggulangan Bencana (BNPB), setidaknya 830 rumah hancur dan 1,249 rusak, dan 5,064 orang mengungsi. ' +
    'Data BPBD Kabupaten Kepulauan Selayar dan hasil pemeriksaan lapangan memperlihatkan bahwa dampak dari kejadian tersebut adalah 1 orang meninggal dunia, ' + 
    '175 orang luka-luka, 358 bangunan rusak berat, 808 bangunan rusak ringan dan 26 bangunan pemerintah rusak. Daerah yang mengalami bencana meliputi ' +
    'Kecamatan Pasimarannu, Pasilambena, Takabonerate, dan Pasimasunggu. Kecamatan Pasimarannu dan Pasilambena merupakan daerah terparah karena lokasinya ' +
    'terletak dekat dengan pusat gempa bumi. ')

st.write('**_Melihat besarnya dampak yang disebabkan oleh Sesar Kalaotoa, pemahaman mengenai sesar baru ini perlu ditingkatkan sebagai upaya mitigasi '+
    'risiko bahaya gempa yang mungkin terjadi di masa yang akan datang._**' )  

st.subheader('Earthquakes Distribution')

col1, col2 = st.columns(2)
with col1:
    #def color_mag(val):
        #color = 'yellow' if val >= 5.0 else 'white'
        #return f'background-color: {color}'
    #st.dataframe(
        #flores_eq.style.applymap(color_mag, subset=['magnitude']).format({'lat': '{:.3f}', 'lon': '{:.3f}', 'depth_km':'{:.3f}', 'magnitude':'{:.3f}'}), 
        #height = 650, 
        #use_container_width = True)
    st.pyplot(fig1)

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
    st.pyplot(fig2)