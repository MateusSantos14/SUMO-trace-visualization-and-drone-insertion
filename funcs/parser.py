import configparser
from ast import literal_eval
from src.Simulation import *  # Import your Simulation class

def parse_config_and_run(config_file):
    """Reads the configuration file and runs the corresponding functions."""
    config = configparser.ConfigParser()
    config.read(config_file)

    # Initialize the simulation
    if "Simulation" in config:
        trace_path = config["Simulation"]["trace_path"]
        simulation = Simulation(trace_path)
    else:
        raise ValueError("Section 'Simulation' not found in the configuration file.")

    # Iterate over sections in the configuration file
    for section in config.sections():
        if section.startswith("DroneCircular"):
            center = literal_eval(config[section]["center"])
            radius_meters = int(config[section]["radius_meters"])
            max_speed = config[section].getint("max_speed", fallback=10)  # Default: 10
            start_angle = config[section].getint("start_angle", fallback=0)  # Default: 0

            simulation.create_drone_circular(center, radius_meters, max_speed, start_angle)
            print(f"Circular drone created with center at {center} and radius {radius_meters}m.")

        elif section.startswith("DroneAngular"):
            start_point = literal_eval(config[section]["start_point"])
            max_length = int(config[section]["max_length"])
            max_turns = config[section].getint("max_turns", fallback=3)  # Default: 3
            angle_alpha = config[section].getint("angle_alpha", fallback=30)  # Default: 30
            max_speed = config[section].getint("max_speed", fallback=10)  # Default: 10

            simulation.create_drone_angular(start_point, max_length, max_turns, angle_alpha, max_speed)
            print(f"Angular drone created with start point at {start_point}.")

        elif section.startswith("DroneTractor"):
            start_point = literal_eval(config[section]["start_point"])
            width_between_tracks = int(config[section]["width_between_tracks"])
            max_length = int(config[section]["max_length"])
            max_turns = int(config[section]["max_turns"])
            orientation = config[section].get("orientation", fallback="horizontal")  # Default: "horizontal"
            max_speed = config[section].getint("max_speed", fallback=10)  # Default: 10

            simulation.create_drone_tractor(start_point, width_between_tracks, max_length, max_turns, orientation, max_speed)
            print(f"Tractor drone created with start point at {start_point}.")

        elif section.startswith("DroneStatic"):
            point = literal_eval(config[section]["point"])

            simulation.create_drone_static(point)
            print(f"Static drone created at point {point}.")

        elif section.startswith("DroneSquare"):
            center_point = literal_eval(config[section]["center_point"])
            side_length = int(config[section]["side_length"])
            angle_degrees = config[section].getint("angle_degrees", fallback=90)  # Default: 90
            max_speed = config[section].getint("max_speed", fallback=10)  # Default: 10

            simulation.create_drone_square(center_point, side_length, angle_degrees, max_speed)
            print(f"Square drone created with center at {center_point}.")

        elif section == "ExportVideo":
            video_directory = config[section]["video_directory"]
            limits_map = literal_eval(config[section].get("limits_map", fallback="0"))  # Default: 0
            only_vants = config[section].getint("only_vants", fallback=0)  # Default: 0

            simulation.export_to_video(video_directory, limits_map, only_vants)
            print(f"Video exported to {video_directory}.mp4.")

        elif section == "ExportXML":
            new_xml_path = config[section]["new_xml_path"]
            geo = config[section].getint("geo", fallback=1)

            simulation.export_timesteps_to_xml(new_xml_path,geo)
            print(f"Simulation exported to {new_xml_path}.")

        elif section == "ChangeLegend":
            old_legend = config[section]["old_legend"]
            new_legend = config[section]["new_legend"]

            simulation.changeLegend(old_legend, new_legend)
            print(f"Legend changed from '{old_legend}' to '{new_legend}'.")

        elif section == "PrintVehicleInfo":
            vehicle_id = config[section]["vehicle_id"]

            simulation.print_all_vehicle_info(vehicle_id)

        elif section == "RemoveVehicle":
            vehicle_id = config[section]["vehicle_id"]

            simulation.removeVehicle(vehicle_id)
            print(f"Vehicle {vehicle_id} removed from the simulation.")

        else:
            print(f"Section '{section}' not recognized. Skipping.")