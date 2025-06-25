import folium

def plot_flight_path(map_obj, path_coords, color="red"):
    """
    Dibuja la ruta de vuelo (lista de coordenadas) sobre el mapa folium.
    path_coords: lista de tuplas (lat, lon)
    """
    folium.PolyLine(path_coords, color=color, weight=4, opacity=0.8).add_to(map_obj)
    # Marcar inicio y fin
    if path_coords:
        folium.Marker(path_coords[0], popup="Inicio", icon=folium.Icon(color="green")).add_to(map_obj)
        folium.Marker(path_coords[-1], popup="Fin", icon=folium.Icon(color="red")).add_to(map_obj)