"""
foliumの動作確認
"""
# ------------------
# モジュールインポート
# ------------------
import folium
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import mercantile


# ------------------
# 定数パラメータ設定
# ------------------
# 渋谷駅
skytree = [35.710063, 139.8107]
# 保存ファイル名
savename = "map_mercantile.html"


# ------------------
# 関数
# ------------------
def make_geo_json(n, e, w, s):
    upper_left = (w, n)
    upper_right = (e, n)
    lower_left = (w, s)
    lower_right = (e, s)
    coordinates = [
        upper_left,
        upper_right,
        lower_right,
        lower_left,
        upper_left
    ]
    geo_json = {"type": "FeatureCollection",
                "properties":{
                    "lower_left": lower_left,
                    "upper_right": upper_right
                },
                "features":[]}
    grid_feature = {
        "type":"Feature",
        "geometry":{
            "type":"Polygon",
            "coordinates": [coordinates],
        }
    }
    geo_json["features"].append(grid_feature)
    return geo_json


def latlon_to_yx(latlon):
    # 東京駅を原点に
    c_lat, c_lon =  35.681194, 139.767056
    kyoku_hankei =  6356752.314
    sekido_hankei = 6378137
    tokyo_hankei = sekido_hankei * np.cos(c_lat * np.pi / 180.0)
    lat = latlon[0]
    lon = latlon[1]
    lon1_to_m = tokyo_hankei * np.pi / 180.
    lat1_to_m = kyoku_hankei * np.pi / 180.
    dy = (lat - c_lat) * lat1_to_m
    dx = (lon - c_lon) * lon1_to_m
    return [dy, dx]


def dist(yx1, yx2):
    d = np.linalg.norm(np.array(yx1)-np.array(yx2))
    return d


# ------------------
#  メイン処理
# ------------------
def main():
    m = folium.Map(location=skytree, zoom_start=18)
    # geojson読み込み
    geojson = r'japan.geojson'
    # m.choropleth(geo_data=geojson,fill_opacity=0.1)
    # 渋谷駅をマーク
    folium.Marker(skytree, popup='Shibuya St.').add_to(m)
    # 渋谷駅の位置情報からquadkeyの上位3層を生成
    lat, lon = skytree
    for i in range(18,21):
        bounds = mercantile.bounds(mercantile.tile(lon, lat, zoom=i))
        print("{:16.12f} {:16.12f} {:16.12f} {:16.12f} {:8.4f}".format(
            *bounds,
            dist(latlon_to_yx([bounds.north, bounds.east]), latlon_to_yx([bounds.north, bounds.west])))
        )
        bounds_gj =  make_geo_json(bounds.north, bounds.east, bounds.west, bounds.south)
        color = plt.cm.Reds(i / 10)
        color = mpl.colors.to_hex(color)
        gj = folium.GeoJson(
            bounds_gj,
            style_function=lambda feature,
            color=color: {
                'fillColor': color,
                'color':"black",
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.3,
            })
        popup = folium.Popup("level {}".format(i))
        gj.add_child(popup)
        m.add_child(gj)
    # 地図をhtml形式で出力
    m.save(outfile=savename)
    print("save to {}".format(savename))


if __name__ == "__main__":
    main()