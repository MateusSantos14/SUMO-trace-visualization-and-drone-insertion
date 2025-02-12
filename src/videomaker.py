import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import contextily as cx
from shapely.geometry import Polygon
import geopandas as gpd

def _create_dataframe_optimized(vector_coordinates, limits_map=0):
    """Optimized dataframe creation combining both default and defined cases."""
    if limits_map == 0:
        # Vectorized operation for coordinates extraction
        coords = np.array([
            (x, y) for vehicle_list in vector_coordinates
            for vehicle_coords_list in vehicle_list
            for x, y in vehicle_coords_list if (x, y) != (0, 0)
        ])
        if coords.size == 0:
            raise ValueError("No valid coordinates found.")
    else:
        coords = np.array(limits_map)
        if coords.shape[1] != 2:
            raise ValueError("Each coordinate should be a tuple (x, y).")

    min_coords = np.min(coords, axis=0)
    max_coords = np.max(coords, axis=0)
    
    polygon = Polygon(np.array([
        [min_coords[0], min_coords[1]],
        [min_coords[0], max_coords[1]],
        [max_coords[0], max_coords[1]],
        [max_coords[0], min_coords[1]],
        [min_coords[0], min_coords[1]]
    ]))

    return gpd.GeoDataFrame({"geometry": [polygon]}, crs="EPSG:4326"), (max_coords[0] - min_coords[0]) / (max_coords[1] - min_coords[1])

def generate_video_with_vector_coordinates_image(
    vector_coordinates, directory_video, names=[], limits_map=0, only_vants=0
):
    # Pre-process data
    if only_vants == 1:
        vector_coordinates = [vector_coordinates[0]]
        names = [names[0]]
    # Create scenario once
    scenario, proportion = _create_dataframe_optimized(vector_coordinates, limits_map)
    # Pre-compute color assignments
    colors = [
        "red", "blue", "green", "orange", "purple", "#8B0000", "#FF6347",
        "crimson", "navy", "#87CEEB", "royalblue", "#228B22", "#00FF00",
        "olive", "#FF8C00", "#FFBF00", "coral", "violet", "lavender", "magenta"
    ]
    
    # Unpack the coordinates and assign colors based on vehicle type
    coordinates_list = []
    color_list = []
    for i in range(len(vector_coordinates)):
        for j in range(len(vector_coordinates[i])):
            coordinates_list.append(vector_coordinates[i][j])
            color_list.append(colors[i % len(colors)])  # Assign color based on vehicle type

    # Set up the figure with optimized settings
    fig, ax = plt.subplots(figsize=(10 * proportion, 10), dpi=75)
    plt.ioff()  # Turn off interactive mode
    # Optimize geometry transformation
    scenario["geometry"] = scenario["geometry"].apply(
        lambda geom: Polygon(np.array(geom.exterior.coords))
    )
    scenario.plot(ax=ax, alpha=0)

    # Create legend more efficiently
    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", label=names[i],
                  markerfacecolor=colors[i], markersize=10)
        for i in range(len(names))
    ]
    ax.legend(handles=legend_handles, loc="upper left")
    # Add basemap
    cx.add_basemap(ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik)
    # Pre-allocate scatter plot
    num_points = len(coordinates_list)
    points = ax.scatter(np.zeros(num_points), np.zeros(num_points), color=color_list, marker="o", s=20)
    # Pre-compute coordinates arrays for all frames
    total_frames = len(coordinates_list[0])
    coordinates_array = np.array([
        [(point[frame][0], point[frame][1]) for point in coordinates_list]
        for frame in range(total_frames)
    ])
    def update(frame):
        points.set_offsets(coordinates_array[frame])
        if frame % 10 == 0:  # Reduce progress updates
            print(f"{round(frame / total_frames * 100, 2)}%")
        return (points,)

    # Configure animation with optimized settings
    ani = FuncAnimation(
        fig,
        update,
        frames=range(total_frames),
        interval=100,
        blit=True,
        cache_frame_data=False  # Reduce memory usage
    )

    # Save with optimized settings
    ani.save(
        directory_video,
        writer='ffmpeg',
        fps=10,
        dpi=75,
        bitrate=-1,  # Let ffmpeg determine optimal bitrate
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p']
    )
    
    plt.close(fig)  # Clean up