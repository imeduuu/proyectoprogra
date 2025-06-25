import folium

class MapBuilder:
    def __init__(self, center=( -38.7359, -72.5904 ), zoom_start=13):
        self.map = folium.Map(location=center, zoom_start=zoom_start)

    def add_node(self, lat, lon, popup=None, color="blue"):
        folium.CircleMarker(
            location=(lat, lon),
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            popup=popup
        ).add_to(self.map)

    def add_edge(self, latlon1, latlon2, color="gray"):
        folium.PolyLine([latlon1, latlon2], color=color, weight=2).add_to(self.map)

    def get_map(self):
        return self.map