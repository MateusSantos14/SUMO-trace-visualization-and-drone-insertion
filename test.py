import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import json
import configparser
from typing import List, Dict, Any
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import contextily as cx
from shapely.geometry import Polygon
import geopandas as gpd

class DroneConfiguratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Pattern Configurator")
        
        # Make window fullscreen
        self.root.state('zoomed')  # For Windows
        # For Linux/Mac, uncomment the following:
        # self.root.attributes('-zoomed', True)
        
        self.trace_file = ""
        self.drones: List[Dict[str, Any]] = []
        self.clicked_points = []
        
        # Create main container with two frames
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Left frame for controls (make it narrower)
        self.control_frame = ttk.Frame(self.main_container, width=300)
        self.control_frame.pack_propagate(False)  # Prevent frame from shrinking
        self.main_container.add(self.control_frame, weight=0)  # weight=0 prevents expansion
        
        # Right frame for map (make it larger)
        self.map_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.map_frame, weight=1)  # weight=1 allows expansion
        
        self.create_gui()
        
    def create_gui(self):
        # Control Frame Elements
        control_frame = self.control_frame
        
        # File selection
        file_frame = ttk.LabelFrame(control_frame, text="File Selection", padding="3")
        file_frame.pack(fill=tk.X, padx=2, pady=2)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=30).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=2)
        
        # Pattern selection
        pattern_frame = ttk.LabelFrame(control_frame, text="Pattern Configuration", padding="3")
        pattern_frame.pack(fill=tk.X, padx=2, pady=2)
        
        ttk.Label(pattern_frame, text="Pattern:").pack(anchor=tk.W)
        self.pattern_var = tk.StringVar()
        patterns = ['circular', 'angular', 'tractor', 'static', 'following', 'square']
        self.pattern_combo = ttk.Combobox(pattern_frame, textvariable=self.pattern_var, values=patterns)
        self.pattern_combo.pack(fill=tk.X, padx=2, pady=2)
        self.pattern_combo.bind('<<ComboboxSelected>>', self.update_parameters_frame)
        
        # Parameters frame
        self.params_frame = ttk.LabelFrame(control_frame, text="Pattern Parameters", padding="3")
        self.params_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Drone list
        list_frame = ttk.LabelFrame(control_frame, text="Configured Drones", padding="3")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Add scrollbar to listbox
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.drone_listbox = tk.Listbox(list_frame, height=10, yscrollcommand=list_scroll.set)
        self.drone_listbox.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.drone_listbox.yview)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=2, pady=2)
        
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_drone).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Generate Config", command=self.generate_config).pack(side=tk.LEFT, padx=2)

    def create_map(self):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            
        # Extract coordinates from XML
        x_coords, y_coords = self.extract_coordinates()
        if not x_coords or not y_coords:
            return
            
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Create polygon for the area
        coordinates_limits = [
            (min_x, min_y),
            (min_x, max_y),
            (max_x, max_y),
            (max_x, min_y),
            (min_x, min_y),
        ]
        polygon = Polygon(coordinates_limits)
        
        # Create GeoDataFrame
        data = {"geometry": [polygon]}
        scenario = gpd.GeoDataFrame(data, crs="EPSG:4326")
        
        # Calculate proportion for figure size
        proportion = (max_x - min_x) / (max_y - min_y)
        
        # Get the screen width and height
        screen_width = self.map_frame.winfo_width()
        screen_height = self.map_frame.winfo_height()
        
        # Calculate figure size based on screen size
        fig_height = screen_height / 100  # Convert pixels to inches (assuming 100 DPI)
        fig_width = fig_height * proportion
        
        # Create figure and plot with larger size
        self.fig, self.ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
        scenario.plot(ax=self.ax, alpha=0)
        
        # Add basemap with higher zoom level
        cx.add_basemap(
            self.ax, 
            crs=scenario.crs, 
            source=cx.providers.OpenStreetMap.Mapnik,
            zoom=15  # Adjust zoom level as needed
        )
        
        # Remove margins to maximize map size
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        # Add existing points
        for point in self.clicked_points:
            self.ax.scatter(point[0], point[1], color='red', s=100, zorder=5)
        
        # Create canvas and add to frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.map_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add click event
        self.canvas.mpl_connect('button_press_event', self.on_map_click)
        
        # Add coordinate display
        self.coord_var = tk.StringVar()
        coord_label = ttk.Label(self.map_frame, textvariable=self.coord_var, background='white')
        coord_label.place(relx=0.01, rely=0.01)  # Position in top-left corner
        self.canvas.mpl_connect('motion_notify_event', self.update_coordinates)

    
    def update_coordinates(self, event):
        if event.inaxes:
            self.coord_var.set(f'x: {event.xdata:.6f}, y: {event.ydata:.6f}')

    def on_map_click(self, event):
        if event.inaxes and self.pattern_var.get():
            x, y = event.xdata, event.ydata
            self.clicked_points.append((x, y))
            self.ax.scatter(x, y, color='red', s=100)
            self.canvas.draw()
            
            # Get current pattern parameters
            pattern = self.pattern_var.get()
            params = {name: var.get() for name, var in self.current_params.items()}
            params['center'] = f"{x:.6f},{y:.6f}"
            
            # Add to drones list
            drone_config = {"pattern": pattern, **params}
            self.drones.append(drone_config)
            
            # Update listbox
            self.drone_listbox.insert(tk.END, f"{pattern} at ({x:.6f}, {y:.6f})")

    def extract_coordinates(self):
        if not self.trace_file:
            return [], []
            
        tree = ET.parse(self.trace_file)
        root = tree.getroot()
        x_coords = []
        y_coords = []
        
        for timestep in root.findall("timestep"):
            for vehicle in timestep.findall("vehicle"):
                x_coords.append(float(vehicle.get("x")))
                y_coords.append(float(vehicle.get("y")))
                
        return x_coords, y_coords

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if filename:
            self.trace_file = filename
            self.file_path.set(filename)
            self.create_map()

    def update_parameters_frame(self, event=None):
        # Clear existing parameters
        for widget in self.params_frame.winfo_children():
            widget.destroy()
            
        pattern = self.pattern_var.get()
        self.current_params = {}
        
        if pattern == 'circular':
            self.add_param('radius_meters', 'Radius (meters)', '40')
            self.add_param('max_speed', 'Max Speed (m/s)', '10')
            self.add_param('start_angle', 'Start Angle (degrees)', '0')
            
        elif pattern == 'angular':
            self.add_param('max_length', 'Max Length (meters)', '40')
            self.add_param('max_turns', 'Max Turns', '3')
            self.add_param('angle_alpha', 'Angle Alpha (degrees)', '30')
            self.add_param('max_speed', 'Max Speed (m/s)', '10')
            
        elif pattern == 'tractor':
            self.add_param('width_between_tracks', 'Width Between Tracks (meters)', '70')
            self.add_param('max_length', 'Max Length (meters)', '100')
            self.add_param('max_turns', 'Max Turns', '6')
            self.add_param('orientation', 'Orientation', 'horizontal', ['horizontal', 'vertical'])
            self.add_param('max_speed', 'Max Speed (m/s)', '10')
            
        elif pattern == 'following':
            self.add_param('vehicle_id', 'Vehicle ID', '')
            self.add_param('offset_distance', 'Offset Distance (meters)', '10')
            self.add_param('max_speed', 'Max Speed (m/s)', '10')
            
        elif pattern == 'square':
            self.add_param('side_length', 'Side Length (meters)', '50')
            self.add_param('angle_degrees', 'Angle (degrees)', '90')
            self.add_param('max_speed', 'Max Speed (m/s)', '10')

    def add_param(self, param_name: str, label: str, default_value: str, values: List[str] = None):
        frame = ttk.Frame(self.params_frame)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=label).pack(side=tk.LEFT)
        
        if values:
            var = tk.StringVar(value=default_value)
            ttk.Combobox(frame, textvariable=var, values=values).pack(side=tk.LEFT, padx=5)
        else:
            var = tk.StringVar(value=default_value)
            ttk.Entry(frame, textvariable=var).pack(side=tk.LEFT, padx=5)
            
        self.current_params[param_name] = var

    def remove_drone(self):
        selection = self.drone_listbox.curselection()
        if selection:
            index = selection[0]
            self.drone_listbox.delete(index)
            self.drones.pop(index)
            self.clicked_points.pop(index)
            
            # Redraw map
            self.create_map()

    def generate_config(self):
        if not self.trace_file:
            messagebox.showerror("Error", "Please select a trace file")
            return
            
        if not self.drones:
            messagebox.showerror("Error", "Please add at least one drone")
            return
            
        config = configparser.ConfigParser()
        
        # Add simulation section
        config['Simulation'] = {
            'trace_path': os.path.basename(self.trace_file)
        }
        
        # Add drone sections
        for i, drone in enumerate(self.drones):
            section_name = f"Drone{drone['pattern'].capitalize()}{i+1}"
            config[section_name] = {k: str(v) for k, v in drone.items()}
            
        # Add export sections
        config['ExportVideo'] = {
            'video_directory': 'output_video',
            'only_vants': '0'
        }
        
        config['ExportXML'] = {
            'new_xml_path': 'output_simulation.xml'
        }
        
        # Save config file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ini",
            filetypes=[("INI files", "*.ini")]
        )
        
        if file_path:
            with open(file_path, 'w') as configfile:
                config.write(configfile)
            messagebox.showinfo("Success", "Configuration file saved successfully!")

def main():
    root = tk.Tk()
    app = DroneConfiguratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()