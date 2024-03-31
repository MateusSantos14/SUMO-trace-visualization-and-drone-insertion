# Vehicle Simulation

This repository contains a Python-based simulation framework for tracking vehicles and drones within a specified environment. The simulation reads vehicle trace data from an XML file, supports dynamic interaction with vehicles, and can generate both visual and data outputs.

## Features

- **Read Vehicle Trace Data**: Load vehicle movements and attributes from an Trace XML file.
- **Drone Simulation**: Simulate drones following a vehicle or moving in a circular path around a specified point.
- **Add Drone or Vehicles**: Make the trace of your Vehicle with code and import it inside a simulation and visualize it.
- **Export Simulation to XML**: Update the original XML file with the current state of the simulation, and make a new XML with self made data.
- **Export to Video**: Generate a video representation of the vehicle and drone movements throughout the simulation.


## Installation

Clone this repository and ensure you have Python installed on your system. The simulation relies on external libraries; install them using the following command:

pip install -r requirements.txt

## How to Use

This guide will walk you through the essential functions of the `Simulation` class.
### Initializing the Simulation

Begin by creating an instance of the `Simulation` class, specifying the path to your Trace XML file. This file should contain the initial vehicle trace data for the simulation.

```python
from simulation import Simulation

# Initialize the simulation with your Trace XML file
simulation = Simulation("path/to/your/trace_file.xml")
# Create a drone that follows a vehicle
simulation.create_drone_following("vehicle_id", offset_distance)
# Create a drone moving in a circular path
simulation.create_drone_circular((latitude, longitude), radius_meters, angular_speed)
# Print all available information for a specific vehicle or drone
simulation.print_all_vehicle_info("vehicle_or_drone_id")
# Export the simulation state to a new XML file
simulation.export_timesteps_to_xml("new_file_path.xml")
# Generate a video from the simulation
simulation.export_to_video("video_file_name")