from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import contextily as cx#Only for image background
from shapely.geometry import Polygon
import geopandas as gpd

def _create_dataframe_default(vector_coordinates):
    min_x = 1000
    max_x = -1000
    min_y = 1000
    max_y = -1000
    for vehicle_list in vector_coordinates:#Iterate over list of types
        for vehicle_coords_list in vehicle_list:#Iterate over list of vehicles
            for vehicle_coords in vehicle_coords_list:#Iterate over pair of vehicles coordinates
                x = vehicle_coords[0]
                y = vehicle_coords[1]
                if x == 0 and y == 0:
                    continue
                if(x<min_x):
                    min_x = x
                if(x>max_x):
                    max_x = x
                if(y<min_y):
                    min_y = y
                if(y>max_y):
                    max_y = y
    coordinates_limits = [
        (min_x,min_y),
        (min_x,max_y),
        (max_x,min_y),
        (max_x,max_y)

    ]
    polygon = Polygon(coordinates_limits)

    # Create a GeoDataFrame with the polygon
    data = {
        "geometry": [polygon]
    }

    data_frame = gpd.GeoDataFrame(data, crs="EPSG:4326")
    print("Build1")
    return data_frame,(max_x-min_x)/(max_y-min_y)

def _create_dataframe_defined(vector_coordinates):
    if len(vector_coordinates) != 2 or any(len(coord) != 2 for coord in vector_coordinates):
        raise ValueError("Input should be a list with two tuples, each containing two coordinates (x, y).")

    coord1, coord2 = vector_coordinates

    # Extrair as coordenadas
    x1, y1 = coord1
    x2, y2 = coord2

    # Calcular os mínimos e máximos para x e y
    min_x = min(x1, x2)
    max_x = max(x1, x2)
    min_y = min(y1, y2)
    max_y = max(y1, y2)

    # Criar as coordenadas do polígono
    coordinates_limits = [
        (min_x, min_y),
        (min_x, max_y),
        (max_x, min_y),
        (max_x, max_y)
    ]

    polygon = Polygon(coordinates_limits)

    # Criar um GeoDataFrame com o polígono
    data = {
        "geometry": [polygon]
    }

    data_frame = gpd.GeoDataFrame(data, crs="EPSG:4326")

    return data_frame, (max_x - min_x) / (max_y - min_y)

def generate_video_with_vector_coordinates_image(vector_coordinates,directory_video,names=[],limits_map=0,only_vants=0):
    if limits_map == 0:
        scenario,proportion = _create_dataframe_default(vector_coordinates)
    else:
        scenario,proportion = _create_dataframe_defined(limits_map)

    #colors
    colors = [
    'red', 'blue', 'green', 'orange', 'purple',
    '#8B0000',  # Dark Red
    '#FF6347',  # Tomato (light red)
    'crimson',
    'navy',
    '#87CEEB',  # Sky Blue
    'royalblue',
    '#228B22',  # Forest Green
    '#00FF00',  # Lime Green
    'olive',
    '#FF8C00',  # Dark Orange
    '#FFBF00',  # Amber
    'coral',
    'violet',
    'lavender',
    'magenta'
    ]   
    substitle_list = []

    #Check if it is only vants
    coordinates_list = []
    if only_vants==1:
        coordinates_list_aux = []
        coordinates_list_aux.append(vector_coordinates[0])
        names_aux = []
        names_aux.append(names[0])
        vector_coordinates = coordinates_list_aux
        names = names_aux

    #Unpack the coordinates
    color_list = []
    substitle_list = []
    markersize_list = []
    for i in range(len(vector_coordinates)):
        for j in range(len(vector_coordinates[i])):
            coordinates_list.append(vector_coordinates[i][j])
            color_list.append(colors[i])
            substitle_list.append(names[i])
            
    # Draw the map
    #fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    fig, ax = plt.subplots(figsize=(10*proportion, 10), dpi=100)

    scenario.plot(ax=ax, alpha=0)

    # Legenda
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', label=names[i], markerfacecolor=colors[i], markersize=10) for i in range(len(names))]
    plt.legend(handles=legend_handles, loc='upper left')

    cx.add_basemap(ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik)

    zeros_vector = [0]*len(coordinates_list)

    points = ax.scatter(zeros_vector.copy(), zeros_vector.copy(), color=color_list, marker='o',s=20)

    total_number_of_frames = len(coordinates_list[0])


    frames = []

    def init():
        points.set_offsets([[0, 0]*len(coordinates_list)])
        return points 


    def update(frame):

        x_values = [point[frame][0] for point in coordinates_list]
        y_values = [point[frame][1] for point in coordinates_list]
        
        points.set_offsets(np.column_stack((x_values, y_values)))  

        print(f"{round(frame/total_number_of_frames*100,2)}%")#Percentage of conclusion
        return points,

    ani = FuncAnimation(fig, update, frames=range(0, total_number_of_frames, 1), init_func=init, interval=100)#Configuração do vídeo
    ani.save(directory_video, writer='ffmpeg')


