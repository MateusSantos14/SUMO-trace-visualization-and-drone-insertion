import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import contextily as cx
from shapely.geometry import Polygon
import geopandas as gpd
import configparser
from matplotlib.widgets import Button, RadioButtons, TextBox

class InteractivePlot:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.x_coords, self.y_coords = self.extract_coordinates(xml_file)
        self.min_x, self.max_x = min(self.x_coords), max(self.x_coords)
        self.min_y, self.max_y = min(self.y_coords), max(self.y_coords)
        self.saved_points = []  # List of tuples: (x, y, pattern, vehicle_id)
        self.markers = []
        self.selected_pattern = "circular"  # Default pattern
        self.vehicle_id = ""  # For DroneFollowing pattern

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
        if event.inaxes:
            if self.selected_pattern == "following":
                # For "following" pattern, we need to prompt for vehicle_id
                self.vehicle_id = self.text_box.text
                if not self.vehicle_id.isdigit():
                    print("Vehicle ID must be a number.")
                    return
                self.saved_points.append((event.xdata, event.ydata, self.selected_pattern, self.vehicle_id))
            else:
                self.saved_points.append((event.xdata, event.ydata, self.selected_pattern, None))
            marker = self.ax.scatter(event.xdata, event.ydata, color="red", s=100)
            self.markers.append(marker)
            print(f"Saved coordinates: {event.xdata:.6f},{event.ydata:.6f} with pattern: {self.selected_pattern}")
            self.fig.canvas.draw()

    def on_confirm(self, event):
        plt.close()

    def on_pattern_select(self, label):
        self.selected_pattern = label
        print(f"Selected pattern: {self.selected_pattern}")

    def generate_config(self):
        config = configparser.ConfigParser()

        # Add Simulation section
        config["Simulation"] = {
            "trace_path": self.xml_file
        }

        # Add Drone sections for each clicked point
        for i, (x, y, pattern, vehicle_id) in enumerate(self.saved_points, start=1):
            if pattern == "circular":
                config[f"DroneCircular{i}"] = {
                    "center": f"{x:.6f}, {y:.6f}",
                    "radius_meters": "40",
                    "max_speed": "10",
                    "num_points": "12",
                    "start_angle": "0"
                }
            elif pattern == "angular":
                config[f"DroneAngular{i}"] = {
                    "start_point": f"{x:.6f}, {y:.6f}",
                    "max_length": "40",
                    "max_turns": "3",
                    "angle_alpha": "30",
                    "max_speed": "10"
                }
            elif pattern == "tractor":
                config[f"DroneTractor{i}"] = {
                    "start_point": f"{x:.6f}, {y:.6f}",
                    "width_between_tracks": "70",
                    "max_length": "100",
                    "max_turns": "6",
                    "orientation": "vertical",
                    "max_speed": "10"
                }
            elif pattern == "static":
                config[f"DroneStatic{i}"] = {
                    "point": f"{x:.6f}, {y:.6f}"
                }
            elif pattern == "following":
                config[f"DroneFollowing{i}"] = {
                    "vehicle_id": vehicle_id,
                    "offset_distance": "10",
                    "max_speed": "10"
                }
            elif pattern == "square":
                config[f"DroneSquare{i}"] = {
                    "center_point": f"{x:.6f}, {y:.6f}",
                    "side_length": "50",
                    "angle_degrees": "90",
                    "max_speed": "10"
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
        self.radio = RadioButtons(ax_radio, ("circular", "angular", "tractor", "static", "following", "square"))
        self.radio.on_clicked(self.on_pattern_select)

        # Add text box for vehicle ID input
        ax_textbox = plt.axes([0.8, 0.05, 0.1, 0.05])
        self.text_box = TextBox(ax_textbox, 'Vehicle ID:', initial="")
        self.text_box.on_submit(lambda text: print(f"Vehicle ID set to: {text}"))

        # Add confirm button
        ax_button = plt.axes([0.8, 0.01, 0.1, 0.075])
        button = Button(ax_button, "Confirm")
        button.on_clicked(self.on_confirm)

        plt.show()

# Usage
xml_file = "manhattan.xml"  # Replace with your XML file path
interactive_plot = InteractivePlot(xml_file)
interactive_plot.show()

# After closing the plot, generate the config file
interactive_plot.generate_config()