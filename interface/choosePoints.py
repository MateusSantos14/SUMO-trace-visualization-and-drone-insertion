import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import configparser
from typing import List, Dict, Any, Tuple
import os
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import contextily as cx
import geopandas as gpd
from shapely.geometry import Polygon, box
import matplotlib.pyplot as plt
from ttkthemes import ThemedTk
import platform
import json
from pathlib import Path
import threading

# Define pattern parameters
PATTERN_PARAMS = {
    'circular': {'radius': 50, 'speed': 10},
    'angular': {'angle': 45, 'speed': 10},
    'tractor': {'width': 100, 'height': 50, 'speed': 10},
    'static': {'speed': 0},
    'following': {'distance': 50, 'speed': 10},
    'square': {'side_length': 100, 'speed': 10}
}

import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt

class DroneConfiguratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Pattern Configurator")
        
        # Initialize variables
        self.trace_file = ""
        self.drones = []
        self.points = []
        self.current_params = {}
        self.coord_to_pixel = None
        self.pixel_to_coord = None
        
        self._setup_ui()
        self._bind_events()
        
    def _setup_ui(self):
        # Main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Control frame
        self.control_frame = self._create_control_frame()
        self.main_container.add(self.control_frame, weight=0)
        
        # Map frame
        self.map_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.map_frame, weight=1)
        
        # Canvas for map
        self.canvas = tk.Canvas(self.map_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Coordinates label
        self.coord_label = ttk.Label(self.map_frame, background='white')
        self.coord_label.place(relx=0.01, rely=0.01)
        
    def _create_control_frame(self):
        frame = ttk.Frame(self.main_container, width=300)
        frame.pack_propagate(False)
        
        # File selection
        file_frame = ttk.LabelFrame(frame, text="File Selection", padding=3)
        file_frame.pack(fill=tk.X, padx=2, pady=2)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self._browse_file).pack(side=tk.LEFT)
        
        # Pattern selection
        pattern_frame = ttk.LabelFrame(frame, text="Pattern Configuration", padding=3)
        pattern_frame.pack(fill=tk.X, padx=2, pady=2)
        
        self.pattern_var = tk.StringVar()
        patterns = ['circular', 'angular', 'tractor', 'static', 'following', 'square']
        pattern_combo = ttk.Combobox(pattern_frame, textvariable=self.pattern_var, values=patterns)
        pattern_combo.pack(fill=tk.X)
        pattern_combo.bind('<<ComboboxSelected>>', self._update_parameters)
        
        # Parameters frame
        self.params_frame = ttk.LabelFrame(frame, text="Parameters", padding=3)
        self.params_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Drone list
        list_frame = ttk.LabelFrame(frame, text="Configured Drones", padding=3)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Treeview for drones
        columns = ('Pattern', 'Location', 'Parameters')
        self.drone_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.drone_tree.heading(col, text=col)
            self.drone_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.drone_tree.yview)
        self.drone_tree.configure(yscrollcommand=scrollbar.set)
        
        self.drone_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=2, pady=2)
        
        ttk.Button(button_frame, text="Remove Selected", 
                  command=self._remove_drone).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Generate Config",
                  command=self._generate_config).pack(side=tk.LEFT, padx=2)
        
        # Following pattern add button (hidden by default)
        self.following_button = ttk.Button(frame, text="Add Following Drone",
                                         command=self._add_following_drone)
        
        return frame
        
    def _bind_events(self):
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<Motion>', self._on_mouse_move)
        
    def _browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if filename:
            self.trace_file = filename
            self.file_path.set(filename)
            self._load_and_display_map()
            
    def _load_and_display_map(self):
        # Extract coordinates
        coords = self._extract_coordinates()
        if not coords:
            return
            
        # Calculate bounds with padding
        x_coords, y_coords = zip(*coords)
        padding = 0.0001  # Adjust as needed
        bounds = (
            min(x_coords) - padding,
            min(y_coords) - padding,
            max(x_coords) + padding,
            max(y_coords) + padding
        )
        
        # Render map directly
        self._render_map(bounds)
        
    def _render_map(self, bounds):
        # Create temporary GeoDataFrame for the area
        area = gpd.GeoDataFrame(
            geometry=[box(*bounds)],
            crs="EPSG:4326"
        )
        
        # Create figure without displaying
        fig, ax = plt.subplots(figsize=(10, 10))
        area.plot(ax=ax, alpha=0)
        cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=19)
        
        # Save to PIL Image
        fig.canvas.draw()
        self.base_image = Image.frombytes(
            "RGBA",
            fig.canvas.get_width_height(),
            fig.canvas.buffer_rgba(),  # New method
        )

        plt.close(fig)
        
        # Update map display
        self._update_map_display()
        
    def _update_map_display(self):
        if not self.base_image:
            return
            
        # Clear canvas
        self.canvas.delete("all")
        
        # Display map
        self.photo = ImageTk.PhotoImage(self.base_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update coordinate transforms
        self._update_coordinate_transforms()
        
        # Redraw points
        self._redraw_points()
        
    def _update_coordinate_transforms(self):
        if not self.base_image:
            return
            
        width, height = self.base_image.size
        min_x, min_y, max_x, max_y = self._get_bounds()
        
        # Create transform functions
        def coord_to_pixel(x, y):
            px = (x - min_x) / (max_x - min_x) * width
            py = height - (y - min_y) / (max_y - min_y) * height
            return px, py
            
        def pixel_to_coord(px, py):
            x = px / width * (max_x - min_x) + min_x
            y = (height - py) / height * (max_y - min_y) + min_y
            return x, y
            
        self.coord_to_pixel = coord_to_pixel
        self.pixel_to_coord = pixel_to_coord
        
    def _get_bounds(self):
        # Extract bounds from the base image
        # This is a placeholder; you need to implement the logic to get the bounds
        return (0, 0, 1, 1)
        
    def _redraw_points(self):
        if not self.coord_to_pixel:
            return
            
        for point in self.points:
            px, py = self.coord_to_pixel(point[0], point[1])
            self._draw_point(px, py)
            
    def _draw_point(self, px, py, color='red'):
        size = 5
        self.canvas.create_oval(
            px-size, py-size, px+size, py+size,
            fill=color, outline=color, tags='point'
        )
        
    def _on_canvas_resize(self, event):
        if self.base_image:
            new_size = (event.width, event.height)
            self.base_image = self.base_image.resize(new_size, Image.ANTIALIAS)
            self._update_map_display()
            
    def _on_canvas_click(self, event):
        if not self.pixel_to_coord or self.pattern_var.get() == 'following':
            return
            
        x, y = self.pixel_to_coord(event.x, event.y)
        self.points.append((x, y))
        self._draw_point(event.x, event.y)
        self._add_drone(x, y)
        
    def _on_mouse_move(self, event):
        if self.pixel_to_coord:
            x, y = self.pixel_to_coord(event.x, event.y)
            self.coord_label.config(text=f'x: {x:.6f}, y: {y:.6f}')
            
    def _extract_coordinates(self):
        if not self.trace_file:
            return None
            
        try:
            tree = ET.parse(self.trace_file)
            coords = []
            
            for timestep in tree.findall("timestep"):
                for vehicle in timestep.findall("vehicle"):
                    coords.append((
                        float(vehicle.get("x")),
                        float(vehicle.get("y"))
                    ))
                    
            return coords
        except Exception as e:
            print(f"Failed to parse trace file: {e}")
            return None
        
    def _update_parameters(self, event=None):
        pattern = self.pattern_var.get()
        
        # Clear existing parameters
        for widget in self.params_frame.winfo_children():
            widget.destroy()
            
        # Show/hide following button
        if pattern == 'following':
            self.following_button.pack(fill=tk.X, padx=2, pady=2)
        else:
            self.following_button.pack_forget()
            
        # Add new parameters based on pattern
        self.current_params = {}
        if pattern in PATTERN_PARAMS:
            for param, default in PATTERN_PARAMS[pattern].items():
                self._add_parameter(param, default)
                
    def _add_parameter(self, name, default):
        frame = ttk.Frame(self.params_frame)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=name).pack(side=tk.LEFT)
        var = tk.StringVar(value=str(default))
        ttk.Entry(frame, textvariable=var).pack(side=tk.LEFT, padx=5)
        
        self.current_params[name] = var
        
    def _add_drone(self, x, y):
        pattern = self.pattern_var.get()
        params = {name: var.get() for name, var in self.current_params.items()}
        params['center'] = f"{x:.6f},{y:.6f}"
        
        self.drones.append({"pattern": pattern, **params})
        
        # Add to treeview
        params_str = ', '.join(f"{k}: {v}" for k, v in params.items() 
                             if k != 'center')
        self.drone_tree.insert('', 'end', values=(
            pattern,
            f"({x:.6f}, {y:.6f})",
            params_str
        ))
        
    def _add_following_drone(self):
        if not self.current_params:
            return
            
        params = {name: var.get() for name, var in self.current_params.items()}
        self.drones.append({"pattern": "following", **params})
        
        # Add to treeview
        params_str = ', '.join(f"{k}: {v}" for k, v in params.items())
        self.drone_tree.insert('', 'end', values=(
            "following",
            "N/A",
            params_str
        ))
        
    def _remove_drone(self):
        selection = self.drone_tree.selection()
        if not selection:
            return
            
        index = self.drone_tree.index(selection[0])
        self.drone_tree.delete(selection[0])
        self.drones.pop(index)
        
        if index < len(self.points):
            self.points.pop(index)
            self._update_map_display()  # Redraw all points
            
    def _generate_config(self):
        if not self.trace_file or not self.drones:
            messagebox.showerror("Error", "Please select a trace file and add drones")
            return
            
        config = configparser.ConfigParser()
        
        config['Simulation'] = {
            'trace_path': os.path.basename(self.trace_file)
        }
        
        for i, drone in enumerate(self.drones):
            section = f"Drone{drone['pattern'].capitalize()}{i+1}"
            config[section] = {k: str(v) for k, v in drone.items()}
            
        config['ExportVideo'] = {
            'video_directory': 'output_video',
            'only_vants': '0'
        }
        config['ExportXML'] = {'new_xml_path': 'output_simulation.xml'}
        
        # Save config
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ini",
            filetypes=[("INI files", "*.ini")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as configfile:
                    config.write(configfile)
                messagebox.showinfo("Success", "Configuration saved!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")

def main():
    root = ThemedTk(theme="arc")
    app = DroneConfiguratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()