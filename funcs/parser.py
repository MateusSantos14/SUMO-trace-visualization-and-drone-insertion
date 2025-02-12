import configparser
from ast import literal_eval
from src.Simulation import *  # Importe sua classe Simulation

def parse_config_and_run(config_file):
    """Lê o arquivo de configuração e executa as funções correspondentes."""
    config = configparser.ConfigParser()
    config.read(config_file)

    # Inicializa a simulação
    if "Simulation" in config:
        trace_path = config["Simulation"]["trace_path"]
        simulation = Simulation(trace_path)
    else:
        raise ValueError("Seção 'Simulation' não encontrada no arquivo de configuração.")

    # Itera sobre as seções do arquivo de configuração
    for section in config.sections():
        if section == "DroneCircular":
            center = literal_eval(config[section]["center"])
            radius_meters = int(config[section]["radius_meters"])
            max_speed = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10
            start_angle = config[section].getint("start_angle", fallback=0)  # Valor padrão: 0

            simulation.create_drone_circular(center, radius_meters, max_speed, start_angle)
            print(f"Drone circular criado com centro em {center} e raio {radius_meters}m.")

        elif section == "DroneAngular":
            start_point = literal_eval(config[section]["start_point"])
            max_length = int(config[section]["max_length"])
            max_turns = config[section].getint("max_turns", fallback=3)  # Valor padrão: 3
            angle_alpha = config[section].getint("angle_alpha", fallback=30)  # Valor padrão: 30
            max_speed = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10

            simulation.create_drone_angular(start_point, max_length, max_turns, angle_alpha, max_speed)
            print(f"Drone angular criado com ponto inicial em {start_point}.")

        elif section == "DroneTractor":
            start_point = literal_eval(config[section]["start_point"])
            width_between_tracks = int(config[section]["width_between_tracks"])
            max_length = int(config[section]["max_length"])
            max_turns = int(config[section]["max_turns"])
            orientation = config[section].get("orientation", fallback="horizontal")  # Valor padrão: "horizontal"
            max_speed = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10

            simulation.create_drone_tractor(start_point, width_between_tracks, max_length, max_turns, orientation, max_speed)
            print(f"Drone trator criado com ponto inicial em {start_point}.")

        elif section == "DroneStatic":
            point = literal_eval(config[section]["point"])

            simulation.create_drone_static(point)
            print(f"Drone estático criado no ponto {point}.")

        elif section == "DroneFollowing":
            vehicle_id = config[section]["vehicle_id"]
            offset_distance = int(config[section]["offset_distance"])
            max_speed = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10

            simulation.create_drone_following(vehicle_id, offset_distance, max_speed)
            print(f"Drone seguindo o veículo {vehicle_id} com offset de {offset_distance}m.")

        elif section == "DroneSquare":
            center_point = literal_eval(config[section]["center_point"])
            side_length = int(config[section]["side_length"])
            angle_degrees = config[section].getint("angle_degrees", fallback=90)  # Valor padrão: 90
            max_speed = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10

            simulation.create_drone_square(center_point, side_length, angle_degrees, max_speed)
            print(f"Drone quadrado criado com centro em {center_point}.")

        elif section == "ExportVideo":
            video_directory = config[section]["video_directory"]
            limits_map = literal_eval(config[section].get("limits_map", fallback="0"))  # Valor padrão: 0
            only_vants = config[section].getint("only_vants", fallback=0)  # Valor padrão: 0

            simulation.export_to_video(video_directory, limits_map, only_vants)
            print(f"Vídeo exportado para {video_directory}.mp4.")

        elif section == "ExportXML":
            new_xml_path = config[section]["new_xml_path"]

            simulation.export_timesteps_to_xml(new_xml_path)
            print(f"Simulação exportada para {new_xml_path}.")

        elif section == "ChangeLegend":
            old_legend = config[section]["old_legend"]
            new_legend = config[section]["new_legend"]

            simulation.changeLegend(old_legend, new_legend)
            print(f"Legenda alterada de '{old_legend}' para '{new_legend}'.")

        elif section == "PrintVehicleInfo":
            vehicle_id = config[section]["vehicle_id"]

            simulation.print_all_vehicle_info(vehicle_id)

        elif section == "RemoveVehicle":
            vehicle_id = config[section]["vehicle_id"]

            simulation.removeVehicle(vehicle_id)
            print(f"Veículo {vehicle_id} removido da simulação.")

        else:
            print(f"Seção '{section}' não reconhecida. Ignorando.")