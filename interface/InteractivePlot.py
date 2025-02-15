import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import contextily as cx
from shapely.geometry import Polygon
import geopandas as gpd
import configparser
from matplotlib.widgets import Button, RadioButtons
import os

#Labels para interface em português
label_dict = {
    'Circular':'circular',
    'Angular':'angular',
    'Trator':'tractor',
    'Estático':'static',
    'Quadrangular':'square'
}

class InteractivePlot:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        # Remove the .xml extension from the file path
        self.base_file_path = os.path.splitext(xml_file)[0]
        self.x_coords, self.y_coords = self.extract_coordinates(xml_file)
        self.min_x, self.max_x = min(self.x_coords), max(self.x_coords)
        self.min_y, self.max_y = min(self.y_coords), max(self.y_coords)
        self.saved_points = []  # List of tuples: (x, y, pattern, vehicle_id)
        self.markers = []
        self.selected_pattern = "circular"  # Default pattern
        self.pattern_counts = {"circular": 0, "angular": 0, "tractor": 0, "static": 0, "square": 0}

    def extract_coordinates(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        x_coords = []
        y_coords = []

        for timestep in root.findall("timestep"):
            for vehicle in timestep.findall("vehicle"):
                x_coords.append(float(vehicle.get("x")))
                y_coords.append(float(vehicle.get("y")))

        return x_coords, y_coords

    def on_mouse_move(self, event):
        if event.inaxes:
            self.text.set_text(f"x: {event.xdata:.6f}, y: {event.ydata:.6f}")
            self.fig.canvas.draw()

    def on_click(self, event):
        # Ignore clicks outside the map area or within UI elements
        if event.inaxes and event.inaxes not in [self.radio.ax, self.button]:
            x, y = event.xdata, event.ydata
            # Check if the coordinates are within the map bounds
            if self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y:
                self.saved_points.append((x, y, self.selected_pattern, None))
                marker = self.ax.scatter(x, y, color="red", s=100)
                self.markers.append(marker)
                print(f"Saved coordinates: {x:.6f},{y:.6f} with pattern: {self.selected_pattern}")
                self.fig.canvas.draw()
            else:
                print(f"Ignored click outside map area: {x:.6f},{y:.6f}") 
    def on_confirm(self, event):
        plt.close()

    def on_pattern_select(self, label):
        self.selected_pattern = label_dict[label]
        print(f"Selected pattern: {self.selected_pattern}")

    def generate_config(self):
        config = configparser.ConfigParser()

        # Add Simulation section
        config["Simulation"] = {
            "trace_path": self.xml_file
        }

        # Add Drone sections for each clicked point
        for i, (x, y, pattern, vehicle_id) in enumerate(self.saved_points, start=1):
            self.pattern_counts[pattern] += 1
            section_name = f"Drone{pattern.capitalize()}{self.pattern_counts[pattern]}"
            if pattern == "circular":
                config[section_name] = {
                    "center": f"{x:.6f}, {y:.6f}",
                    "radius_meters": "40",
                    "max_speed": "10",
                    "num_points": "12",
                    "start_angle": "0"
                }
            elif pattern == "angular":
                config[section_name] = {
                    "start_point": f"{x:.6f}, {y:.6f}",
                    "max_length": "40",
                    "start_angle": "0",
                    "max_turns": "3",
                    "angle_alpha": "30",
                    "max_speed": "10"
                }
            elif pattern == "tractor":
                config[section_name] = {
                    "start_point": f"{x:.6f}, {y:.6f}",
                    "width_between_tracks": "70",
                    "max_length": "100",
                    "max_turns": "6",
                    "orientation": "vertical",
                    "max_speed": "10"
                }
            elif pattern == "static":
                config[section_name] = {
                    "point": f"{x:.6f}, {y:.6f}"
                }
            elif pattern == "square":
                config[section_name] = {
                    "center_point": f"{x:.6f}, {y:.6f}",
                    "side_length": "50",
                    "angle_degrees": "90",
                    "max_speed": "10"
                }

        # Use the base_file_path (without .xml) for ExportXML and ExportVideo
        config["ExportXML"] = {
            "new_xml_path": f"{self.base_file_path}UAV.xml"
        }
        config["ExportVideo"] = {
            "video_directory": f"{self.base_file_path}_video",
            "only_vants": 0,
        }

        # Save the config file
        with open("config.ini", "w") as configfile:
            config.write(configfile)
        print("Config file 'config.ini' generated.")

    def show(self):
        coordinates_limits = [
            (self.min_x, self.min_y),
            (self.min_x, self.max_y),
            (self.max_x, self.max_y),
            (self.max_x, self.min_y),
            (self.min_x, self.min_y),
        ]
        polygon = Polygon(coordinates_limits)

        # Create a GeoDataFrame with the polygon
        data = {"geometry": [polygon]}
        scenario = gpd.GeoDataFrame(data, crs="EPSG:4326")
        proportion = (self.max_x - self.min_x) / (self.max_y - self.min_y)
        self.fig, self.ax = plt.subplots(figsize=(10 * proportion, 10), dpi=100)
        scenario.plot(ax=self.ax, alpha=0)
        cx.add_basemap(
            self.ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik
        )

        # Connect events
        self.cid_move = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.on_mouse_move
        )
        self.cid_click = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_click
        )
        self.text = self.ax.text(0.05, 0.95, "", transform=self.ax.transAxes)

        # Add pattern selection radio buttons
        ax_radio = plt.axes([0.8, 0.1, 0.15, 0.2])
        self.radio = RadioButtons(ax_radio, list(label_dict.keys()))
        self.radio.on_clicked(self.on_pattern_select)

        # Add confirm button
        ax_button = plt.axes([0.8, 0.01, 0.1, 0.075])
        self.button = Button(ax_button, "Confirm")
        self.button.on_clicked(self.on_confirm)

        plt.show()

def run(path):
    # Usage
    xml_file = path  # Replace with your XML file path
    interactive_plot = InteractivePlot(xml_file)
    interactive_plot.show()

    # After closing the plot, generate the config file
    interactive_plot.generate_config()