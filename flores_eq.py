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

# made by Putri Natari Ratna
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
plt.title('Magnitude vs Time', size = 16)
ax.annotate('Gempa utama', (datetime.strptime('2021-12-14','%Y-%m-%d'),7.4), size=14)
ax.plot([datetime.strptime('2021-12-14','%Y-%m-%d'), datetime.strptime('2022-03-20','%Y-%m-%d')],[6.0,6.0],
       color='green', linestyle='--')
ax.annotate('Gempa susulan', (datetime.strptime('2022-01-25','%Y-%m-%d'),6.1), size=14)
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

### mapping
centroids = flores_latlong.groupby(['predicted_label']).mean().reset_index()
centroid = centroids.sort_values('lon', ascending=True).reset_index(drop=True).reset_index()

mapping = dict(zip(centroid['predicted_label'], centroid['index']))

flores_mapping = flores_latlong.copy()
flores_mapping['predicted_label'] = flores_mapping['predicted_label'].apply(lambda x: mapping[x])


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
    filtered = flores_mapping[flores_mapping['predicted_label']==i]
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

#fig3 = plt.figure(figsize=[12,8])

### basemap
#m = Basemap(resolution='i',
 #           llcrnrlat=-9.2,urcrnrlat=-6.0,llcrnrlon=119.5,urcrnrlon=123.5)
#m.shadedrelief()
#plt.yticks(np.arange(-9.2, -6.0, step=1))
#plt.xticks(np.arange(119.5, 123.5, step=1))

### scatter and segment
#for i in np.sort(np.unique(clusterer.labels_)):
 #   filtered = flores_latlong[flores_latlong['predicted_label']==i]
  #  filtered_long = filtered['lon']
   # filtered_lat = filtered['lat']
    
    #scatter = plt.scatter(filtered_long, filtered_lat, c=colors[i],label='Cluster ' + str(i + 1))
    
#plt.xlabel('Longitude')
#plt.ylabel('Latitude')
#plt.title('Segments of Kalaotoa Fault based on clustered eartquakes')
#plt.legend()
#plt.show()

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
    st.metric('Jumlah infrastruktur yang rusak', 2079)

col11, col12 = st.columns(2)
with col11:
    image = Image.open('warga_mengungsi.jpeg')
    st.image(image, caption='Gambar 1. Warga Pulau Selayar yang mengungsi akibat gempa 14 Desember 2021 (BPBD)')

with col12:

    st.write('Telah terjadi gempa pada hari Selasa, 14 Desember 2021 pukul 10:20:23 WIB dengan magnitudo 7.3. Pusat gempa terletak di Laut Flores ' +
    'pada koordinat 7.59°LS dan 122.24°BT pada kedalaman 10 km dan berjarak sekitar 115 km utara Kota Maumere (ibu kota Kabupaten Sikka), ' +
    'Provinsi Nusa Tenggara Timur, atau berjarak sekitar 256.6 km tenggara Kota Benteng (ibu kota Kabupaten Kepulauan Selayar), Provinsi Sulawesi Selatan. ' +
    'Dilihat dari mekanisme sumbernya, gempa ini dipicu oleh aktivitas **_Sesar Kalaotoa_**, sebuah sesar geser yang sebelumnya tidak diketahui keberadaannya. ' +
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

st.subheader('Informasi Seputar Gempa')

col1, col2 = st.columns(2)
with col1:
    start_time = dt.date(2021,12,14)
    end_time = dt.date(2022,3,20)

    select_period = st.slider('Select period:', min_value=start_time, max_value=end_time, value= start_time)

    st.write('Distribusi gempa pada periode: ', start_time, 'to ', select_period)

    # Filter data between two dates
    filtered_df = flores_eq.loc[(flores_eq['date'] >= start_time) & (flores_eq['date'] <= select_period)]
    print(filtered_df.tail())

    st.map(filtered_df)
    st.caption('Gambar 2. Distrisbusi gempa susulan akibat Gempa Laut Flores 2021')

with col2:
    #def color_mag(val):
        #color = 'yellow' if val >= 5.0 else 'white'
        #return f'background-color: {color}'
    #st.dataframe(
        #flores_eq.style.applymap(color_mag, subset=['magnitude']).format({'lat': '{:.3f}', 'lon': '{:.3f}', 'depth_km':'{:.3f}', 'magnitude':'{:.3f}'}), 
        #height = 650, 
        #use_container_width = True)
    st.info('**NOTE**' + '\n' '- Geser slider untuk melihat distribusi gempa susulan pada rentang waktu tertentu' + '\n'
    '- Lingkaran merah menunjukkan gempa yang terjadi')
    

    st.write('Kejadian gempa utama tanggal 14 Desember 2021 di Laut FLores diikuti oleh serangkaian kejadian gempa susulan. ' + 
    'Hingga tanggal 20 Maret 2022 telah terjadi 1403 kali gempa susulan dengan magnitudo berkisar antara Mw 1.9 hingga Mw 5.9. ' +
    'Dapat dilihat pada Gambar 2, gempa susulan terdistribusi dalam arah barat barat laut hingga timur tenggara akibat adanya slip ' +
    'menganan dari aktivitas Sesar Kalaotoa. Gempa susulan ini juga memicu terjadinya gempa di Sesar Selayar yang merupakan ' +
    'sesar normal yang terletak di sebelah barat Sesar Kalaotoa. Gempa di Sesar Selayar tersebut diyakini sebagai akibat dari transfer stress ' +
    'dari Gempa Laut Flores 2021')

col5, col6 = st.columns(2)
with col5:
    st.info('**NOTE**' + '\n' '- _Chart_ di samping menunjukkan hubungan jumlah dan magnitudo gempa susulan dengan waktu' + '\n'
    '- Garis putus-putus hijau menunjukkan rentang waktu terjadinya gempa susulan')
    
    st.write('Berdasarkan pemodelan _finite fault_ yang dilakukan oleh ANSS, proses _rupture_ terjadi pada sesar dengan dimensi 90 km x 40 km ' + 
    'dengan maksimum slip _coseismic_ sebesar 4 meter. Dengan besarnya dimensi tersebut, sesar membutuhkan waktu untuk dapat kembali ke kesetimbangan ' +
    'setelah melepaskan energi berupa gempa bermagnitudo 7.3. Hal ini dapat terlihat dari jumlah dan magnitudo dari gempa susulan yang terus menurun ' +
    'seperti yang ditunjukkan oleh Gambar 3.')

with col6:
    st.pyplot(fig1)
    st.caption('Gambar 3. Hubungan jumlah dan besar magnitudo dari gempa susulan dengan waktu')
    

with st.expander("Data Gempa Laut Flores 2021"):
    def color_mag(val):
        color = 'yellow' if val >= 5.0 else 'white'
        return f'background-color: {color}'
    st.dataframe(
        flores_eq.style.applymap(color_mag, subset=['magnitude']).format({'lat': '{:.3f}', 'lon': '{:.3f}', 'depth_km':'{:.3f}', 'magnitude':'{:.3f}'}), 
        height = 200, 
        use_container_width = True)


st.subheader('Tiga Segmen Sesar Kalaotoa')

col3, col4 = st.columns(2)
with col3:
    st.write('Sebuah tim yang dipimpin oleh Pepen Supendi di University of Cambridge, Inggris, menganalisis kedalaman dan ' +
    'lokasi gempa utama, serta 1.400 gempa susulan dari Gempa Laut Flores 2021. ' + 
    'Distribusi gempa susulan menunjukkan pola yang menarik, dengan setidaknya terdapat tiga cluster (Gambar 4) yang berkaitan dengan gempa utama Mw 7.3. ' +
    'Cluster 2 disebabkan oleh slip pada sesar utama (segment 2) berorientasi timur-barat sepanjang ~100 km yang juga menyebabkan gempa Mw 7.3. Segment ini memicu ' +
    'gempa pada segmen 3 (cluster 3) yang berorientasi tenggara sepanjang ~40 km di timur serta gempa pada segment 1 (cluster 1) yang berorientasi barat laut sepanjang ' +
    '~50 km di barat. Berdasarkan analisis visual dari sebaran gempa susulan, lebar dari ketiga segmen ini adalah ~20 km.')

    st.write('Kemudian, lokasi dari segment-segment sesar ini juga berdekatan dengan sesar lainnya yang tergolong aktif. Segment 1 yang berada di paling barat ' +
    'berada di ujung atau dekat dengan Sesar Selayar, sementara Segment 3 yang berada di bagian tenggara dekat dengan _central back-arc thrust_. ' +
    'Oleh karena itu, pergerakan dari segment-segment ini dapat memengaruhi atau memicu terjadinya gempa dari sumber-sumber gempa lainnya. ' +
    'Identifikasi dan pemahaman sistem sesar baru ini merupakan tantangan besar, tetapi hal ini sangat penting jika kita ingin memahami bahaya seismik di Indonesia bagian timur.' )

    st.info('**Note:**' + '\n' 'Sesar Selayar dan _central back-arc thrust_ tidak diperlihatkan pada Gambar 4.' + '\n'
    'Struktur geologi di sekitar Laut Flores dapat dilihat pada link berikut: https://www.greeners.co/wp-content/uploads/2018/08/Para-Ahli-Aktivitas-Flores-Back-Arc-Thrust-Penyebab-Gempa-Lombok_02.jpg')

with col4:
    #segment_cek = st.checkbox('Segment Sesar Kalaotoa')
    #if segment_cek:
        #st.pyplot(fig2)
    #else:
    st.pyplot(fig2)
    st.caption('Gambar 4. Segment Sesar Kalaotoa berdasarkan klusterisasi gempa')

st.subheader('Kesimpulan')
st.write('- Gempa Laut Flores Mw 7.3 dan gempa susulannya disebabkan oleh slip yang terjadi di sepanjang sistem Sesar Kalaotoa (sesar geser menganan) yang baru teridentifikasi.')
st.write('- Gempa susulan terdistribusi dalam arah barat barat laut hingga timur tenggara.')
st.write('- Distribusi gempa dapat dibagi menjadi tiga cluster yang mengindikasikan adanya tiga segmen sesar.')
st.write('- Sesar Kalaotoa dapat dibagi menjadi tiga segment: Segment 1 (50 km) berorientasi barat laut; Segment 2 (100 km) berorientasi timur-barat; dan ' + 
'Segment 3 (40 km) berorientasi tenggara.')
st.write('- Daerah Kabupaten Kepulauan Selayar dan Kota Maumere tergolong rawan gempa bumi dan tsunami karena terletak dekat dengan sumber gempa bumi yaitu sesar aktif berupa sesar ' +
'mendatar (Sesar Selayar dan Sesar Kalaotoa) dan _central back-arc thrust_ di Laut Flores, serta sumber pembangkit tsunami yaitu _central back-arc thrust_.')


st.subheader('Rekomendasi')
st.write('- Pulau Selayar dan Pulau Flores tergolong kawasan rawan bencana geologi (gempa bumi dan tsunami). Oleh karena itu, upaya mitigasi bencana geologi secara struktural dan non struktural harus ditingkatkan. ' +
'Mitigasi struktural dilakukan dengan membangun bangunan tahan gempa bumi, tempat dan jalur evakuasi, membangun tanggul pantai, menanam vegetasi pantai, dan lain-lain. Mitigasi non struktural dilakukan dengan ' +
'meningkatkan kapasitas masyarakat dan aparat dalam menghadapi bencana geologi, misalnya : sosialisasi, simulasi dan wajib latih.')
st.write('- Bangunan vital, strategis dan mengundang konsentrasi banyak orang agar dibangun mengikuti kaidah – kaidah bangunan tahan gempa bumi; menghindari membangun pada tanah urugan yang tidak memenuhi persyaratan ' + 
'teknis karena rawan terhadap guncangan gempa bumi; menghindari membangun pada bagian atas punggungan, tebing lereng terjal yang telah mengalami pelapukan dan tanah menjadi gembur karena akan berpotensi terjadinya ' +
'gerakan tanah yang dipicu oleh guncangan gempa bumi kuat dan curah hujan tinggi.')
st.write('- Pemerintah Provinsi Sulawesi Selatan, Pemerintah Kabupaten Kepulauan Selayar, dan Pemerintah Provinsi Nusa Tenggara Timur direkomendasikan memasukkan materi kebencanaan geologi (gempa bumi, tsunami, letusan gunung api ' +
'dan gerakan tanah) ke dalam kurikulum pendidikan agar para guru dan pelajar dapat memperoleh pengetahuan tentang mitigasi bencana geologi.')
st.write('- Analisis _slip rate_ dan analisis seismotektonik menggunakan data GPS, data _bathymetri_, lintasan seismik, sebaran kegempaan, dan lain-lain diperlukan untuk memahami potensi bahaya seismik sehingga dapat dilakukan ' +
'pemutakhiran peta Kawasan Rawan Bencana (KRB) gempa Pulau Selayar dan Pulau Flores).')

st.subheader('Referensi')
st.caption('Supendi, P., Rawlinson, N., Prayitno, B. S., Widiyantoro, S., Simanjuntak, A., Palgunadi, K. H., Kurniawan, A., Marliyani, G. I., Nugraha, A. D., Daryono, D., Anugrah, S. D., Fatchurochman, I., Gunawan, M. T., ' +
'Sadly, M., Adi, S. P., Karnawati, D., & Arimuko, A. (2022). The Kalaotoa Fault: A Newly Identified Fault that Generated the Mw 7.3 Flores Sea Earthquake. The Seismic Record, 2(3), 176–185. https://doi.org/10.1785/0320220015')
st.caption('https://vsi.esdm.go.id/index.php/gempabumi-a-tsunami/laporan-singkat-dan-rekomendasi-teknis/3903-laporan-singkat-dan-rekomendasi-teknis-gempa-bumi-tanggal-14-desember-2021-di-kabupaten-kepulauan-selayar-provinsi-sulawesi-selatan ' + 
'diakses Oktober 2022')
st.caption('https://cdn.bmkg.go.id/Web/Ulasan_gempabumi_14_Desember_2021_102023WIB_M7.4.pdf diakses Oktober 2022')
st.caption('https://earthquake.usgs.gov/earthquakes/eventpage/at00r435a2/executive diakses Oktober 2022')
st.caption('https://www.nature.com/articles/d41586-022-02134-8 diakses Oktober 2022')
st.caption('https://bnpb.go.id/berita/-update-sebanyak-3-900-warga-kabupaten-kepulauan-selayar-mengungsi-akibat-gempabumi-m-7-4-di-laut-flores diakses Oktober 2022')
st.caption('https://www.beritasatu.com/archive/868471/gempa-flores-5064-warga-mengungsi-dan-736-rumah-rusak diakses Oktober 2022')
st.caption('https://en.wikipedia.org/wiki/2021_Flores_earthquake diakses Oktober 2022')
st.caption('https://www.greeners.co/berita/para-ahli-aktivitas-flores-back-arc-thrust-penyebab-gempa-lombok/ diakses Oktober 2022')