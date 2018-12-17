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


# ------------------
# 定数パラメータ設定
# ------------------
# 横浜駅
yokohama_st = [35.466004, 139.622539]
# 渋谷駅
shibuya_st = [35.658047, 139.701664]
# 上野駅
ueno_st = [35.714167, 139.777383]
# 保存ファイル名
savename = "map.html"


# ------------------
# 関数
# ------------------
def get_geojson_grid(upper_right, lower_left, n=6):
    """Returns a grid of geojson rectangles, and computes the exposure in each section of the grid based on the vessel data.

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids" (the default is the upper right hand [lat, lon] of the USA).

    lower_left: array_like
        The lower left hand corner of "grid of grids"  (the default is the lower left hand [lat, lon] of the USA).

    n: integer
        The number of rows/columns in the (n,n) grid.

    Returns
    -------

    list
        List of "geojson style" dictionary objects   
    """
    all_boxes = []
    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)
    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]
    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]
            # Define json coordinates for polygon
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
            all_boxes.append(geo_json)
    return all_boxes


# ------------------
#  メイン処理
# ------------------
def main():
    m = folium.Map(location=shibuya_st, zoom_start=11)
    # geojson読み込み
    geojson = r'japan.geojson'
    m.choropleth(geo_data=geojson,fill_opacity=0.1)
    # 横浜駅、上野駅、渋谷駅をマーク
    folium.Marker(yokohama_st, popup='Yokohama St.').add_to(m)
    folium.Marker(ueno_st, popup='Ueno St.').add_to(m)
    folium.Marker(shibuya_st, popup='Shibuya St.').add_to(m)
    # グリッドを生成
    grid = get_geojson_grid(ueno_st, shibuya_st , n=6)
    for i, geo_json in enumerate(grid):
        color = plt.cm.Reds(i / len(grid))
        color = mpl.colors.to_hex(color)
        gj = folium.GeoJson(
            geo_json,
            style_function=lambda feature,
            color=color: {
                'fillColor': color,
                'color':"black",
                'weight': 0,
                #'dashArray': '10, 2',
                'fillOpacity': 0.5,
            })
        popup = folium.Popup("hoge {}".format(i))
        gj.add_child(popup)
        m.add_child(gj)
    # 地図をhtml形式で出力
    m.save(outfile=savename)
    print("save to {}".format(savename))


if __name__ == "__main__":
    main()