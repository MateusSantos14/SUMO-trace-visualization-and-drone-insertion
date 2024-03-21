from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import contextily as cx#Only for image background
from shapely.geometry import Polygon
import geopandas as gpd

def _create_dataframe(vector_coordinates):
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
    return data_frame

def generate_video_with_vector_coordinates_image(vector_coordinates,directory_video,names=[]):
    
    scenario = _create_dataframe(vector_coordinates)

    #colors
    colors = [
    'red', 'blue', 'green', 'orange', 'purple', 
    'dark red', 'light red', 'crimson', 
    'navy blue', 'sky blue', 'royal blue', 
    'forest green', 'lime green', 'olive', 
    'dark orange', 'amber', 'coral', 
    'violet', 'lavender', 'magenta'
    ]
    substitle_list = []

    #Unpack the coordinates
    coordinates_list = []
    color_list = []
    substitle_list = []
    markersize_list = []
    for i in range(len(vector_coordinates)):
        for j in range(len(vector_coordinates[i])):
            coordinates_list.append(vector_coordinates[i][j])
            color_list.append(colors[i])
            substitle_list.append(names[i])
            
    # Draw the map
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)

    scenario.plot(ax=ax, alpha=0)

    # Legenda
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', label=names[i], markerfacecolor=colors[i], markersize=10) for i in range(len(names))]
    plt.legend(handles=legend_handles, loc='upper left')

    cx.add_basemap(ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik)

    print(color_list)

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

        #print(frame)

        return points,

    ani = FuncAnimation(fig, update, frames=range(0, total_number_of_frames, 1), init_func=init, interval=100)#Configuração do vídeo
    ani.save(directory_video, writer='ffmpeg')


