import folium

def main():
    # 地図の基準として兵庫県明石市を設定
    japan_location = [35, 135]
    m = folium.Map(location=japan_location, zoom_start=5)
    geojson = r'japan.geojson'
    # geojson読み込み
    m.choropleth(geo_data=geojson)
    # 横浜駅をマーク
    yokohama_st = [35.466004, 139.622539]
    folium.Marker(yokohama_st, popup='Yokohama St.').add_to(m)
    # 地図をhtml形式で出力
    m.save(outfile="map.html")

if __name__ == "__main__":
    main()