import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
import contextily as cx#Only for image background
from shapely.geometry import Polygon
import geopandas as gpd


class InteractivePlot:
    def __init__(self, xml_file):
        self.x_coords, self.y_coords = self.extract_coordinates(xml_file)
        self.min_x, self.max_x = min(self.x_coords), max(self.x_coords)
        self.min_y, self.max_y = min(self.y_coords), max(self.y_coords)
        self.saved_x = []
        self.saved_y = []

    def extract_coordinates(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        x_coords = []
        y_coords = []

        for timestep in root.findall('timestep'):
            for vehicle in timestep.findall('vehicle'):
                x_coords.append(float(vehicle.get('x')))
                y_coords.append(float(vehicle.get('y')))
        
        return x_coords, y_coords

    def on_mouse_move(self, event):
        if event.inaxes:
            self.text.set_text(f'x: {event.xdata:.6f}, y: {event.ydata:.6f}')
            self.fig.canvas.draw()

    def on_click(self, event):
        if event.inaxes:
            self.saved_x.append(event.xdata)
            self.saved_y.append(event.ydata)
            print(f'Saved coordinates: {event.xdata:.6f},{event.ydata:.6f}')

    def show(self):
        coordinates_limits = [
            (self.min_x, self.min_y),
            (self.min_x, self.max_y),
            (self.max_x, self.max_y),
            (self.max_x, self.min_y),
            (self.min_x, self.min_y)
        ]
        polygon = Polygon(coordinates_limits)

        # Create a GeoDataFrame with the polygon
        data = {
            "geometry": [polygon]
        }
        scenario = gpd.GeoDataFrame(data, crs="EPSG:4326")
        proportion = (self.max_x - self.min_x) / (self.max_y - self.min_y)
        self.fig, self.ax = plt.subplots(figsize=(10 * proportion, 10), dpi=100)
        scenario.plot(ax=self.ax, alpha=0)
        cx.add_basemap(self.ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik)
        
        # Conectando eventos ao gráfico correto
        self.cid_move = self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.text = self.ax.text(0.05, 0.95, '', transform=self.ax.transAxes)
        
        plt.show()

# Usage
xml_file = 'manhattan.xml'  # Replace with your XML file path
interactive_plot = InteractivePlot(xml_file)
interactive_plot.show()

# Saved coordinates are in interactive_plot.saved_x and interactive_plot.saved_y
