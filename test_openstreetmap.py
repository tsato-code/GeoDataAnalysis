"""
以下からbasemapをダウンロード、インストール
https://github.com/matplotlib/basemap/releases/
"""
import sys
import pandas as pd
from http.client import IncompleteRead
import time

def fetch_latlon():
    url = 'http://qiita.com/butchi_y/items/3a6b70b38e13dc56ef13'
    data = pd.read_html(url)[0]
    data.columns = ['name', 'lat', 'lon']
    return data

def fetch_passenger():
    # fetch data
    urls = ['http://www.jreast.co.jp/passenger/index.html', 'http://www.jreast.co.jp/passenger/2014_01.html']
    data = pd.DataFrame()
    for url in urls:
        df = None
        for i in range(5):
            try:
                df = pd.read_html(url)
                break
            except IncompleteRead as ir:
                time.sleep(0.1)
        # Sometimes fetching passenger fails
        if df is None:
            print('Failed to fetch passenger.')
            sys.exit(1)

        for i in range(2):
            # Delete rank column in the first table
            if url == urls[0]:
                df[i] = df[i].iloc[:, 1:]
                df[i].columns = [col for col in range(len(df[i].columns))]
            data = data.append(df[i])
    # arrange data
    data = data.iloc[2:, [0, 3]]
    data.columns = ['name', 'passenger']
    data.reset_index(inplace=True, drop=True)
    return data


def fetch_data():
    latlon = fetch_latlon()
    passenger = fetch_passenger()
    data = latlon.merge(passenger, how='inner', on='name')
    return data

data = fetch_data()

# =============================================================================
# 地図上にプロット
# =============================================================================
import requests
from io import BytesIO
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from PIL import Image
#%matplotlib inline

# min/max circle size of plot
min_size = 200
max_size = 2000

# Retrive static OpenStreetMap
def get_osm_img(minlat, minlon, maxlat, maxlon, scale=60000, img_format='png'):
    url = 'http://www.openstreetmap.org/export/finish'
    payload = {
        'mapnik_format': img_format, 
        'mapnik_scale': scale, 
        'minlon': minlon, 
        'minlat': minlat, 
        'maxlon': maxlon, 
        'maxlat': maxlat, 
        'format': 'mapnik'
    }
    response = requests.post(url, payload)
    return Image.open(BytesIO(response.content))

fig = plt.figure(figsize=(15, 15))

minlat, minlon, maxlat, maxlon = 35.61, 139.67, 35.75, 139.80
bmap = Basemap(projection='merc', llcrnrlat=minlat, urcrnrlat=maxlat, llcrnrlon=minlon, urcrnrlon=maxlon, lat_ts=0, resolution='l')

x, y = bmap(data['lon'].values, data['lat'].values)

file_name = 'osm.png'
bg_img = None
try:
    bg_img = Image.open(file_name)
except FileNotFoundError as fnfe:
    bg_img = get_osm_img(minlat=minlat, minlon=minlon, maxlat=maxlat, maxlon=maxlon, scale=60000)
    bg_img.save(file_name)
bmap.imshow(bg_img, origin='upper')
bmap.scatter(x, y, c=data['passenger'], cmap=plt.cm.get_cmap('seismic'), alpha=0.5, s=data['passenger'].map(lambda x: (x - data['passenger'].min()) / (data['passenger'].max() - data['passenger'].min()) * (max_size - min_size) + min_size))

# plt.colorbar()
plt.show()
# plt.savefig('out.png')