import math
from Vehicle import Vehicle

earth_radius = 6371000  # Meters

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the Earth's surface given their latitude and longitude.
    """
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius * c

def calculate_angle(p1, p2):
    """
    Calculate the bearing between two points on the Earth's surface.
    """
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    angle = math.atan2(x, y)
    return angle

def limit_speed(start_point, end_point, max_distance):
    """
    Limit the distance between two points to the max_distance, preserving direction.
    """
    distance = haversine_distance(start_point[0], start_point[1], end_point[0], end_point[1])
    if distance > max_distance:
        ratio = max_distance / distance
        lat = start_point[0] + (end_point[0] - start_point[0]) * ratio
        lon = start_point[1] + (end_point[1] - start_point[1]) * ratio
        return (lat, lon)
    else:
        return end_point

def generate_drone_coordinates(vehicle_coordinates, offset_distance, max_speed, smoothing_factor=0.4):
    """
    Generate drone coordinates based on the vehicle coordinates and offset distance.

    Parameters:
    - vehicle_coordinates (list of tuples): List of (lat, lon) coordinates for the vehicle path.
    - offset_distance (float): Distance between the vehicle and the drone in meters.
    - max_speed (float): Maximum speed of the drone in meters per second.
    - smoothing_factor (float): Smoothing factor for gentle movement. Value between 0 and 1.

    Returns:
    - list of tuples: List of (lat, lon, speed) coordinates for the drone path.
    """
    
    drone_coordinates = []
    first_non_zero_coordinate = False
    previous_time = 0  

    for i, vehicle_position in enumerate(vehicle_coordinates):
        current_time = i 
        
        if vehicle_position != (0, 0) and not first_non_zero_coordinate:
            first_non_zero_coordinate = True
            drone_coordinates.append((vehicle_position[0], vehicle_position[1], 0))
            previous_time = current_time
            continue

        if vehicle_position == (0, 0):
            drone_coordinates.append((0, 0, 0))
            continue

        if i < len(vehicle_coordinates) - 1:
            angle = calculate_angle(vehicle_coordinates[i], vehicle_coordinates[i + 1])
        else:
            angle = calculate_angle(vehicle_coordinates[i - 1], vehicle_coordinates[i])

        if angle is None and i > 0:
            drone_coordinates.append(drone_coordinates[-1])
        else:
            lat = vehicle_position[0] - (offset_distance / earth_radius) * (180 / math.pi) * math.cos(angle)
            lon = vehicle_position[1] - (offset_distance / earth_radius) * (180 / math.pi) / math.cos(math.radians(vehicle_position[0])) * math.sin(angle)

            current_lat, current_lon, _ = drone_coordinates[-1]
            smoothed_lat = current_lat + smoothing_factor * (lat - current_lat)
            smoothed_lon = current_lon + smoothing_factor * (lon - current_lon)

            next_drone_position = (smoothed_lat, smoothed_lon)
            limited_drone_position = limit_speed((current_lat, current_lon), next_drone_position, max_speed)

            # Calculate speed
            distance = haversine_distance(current_lat, current_lon, limited_drone_position[0], limited_drone_position[1])
            speed = distance / (current_time - previous_time)
            speed = round(speed, 2)  

            drone_coordinates.append((limited_drone_position[0], limited_drone_position[1], speed))
            previous_time = current_time

    return drone_coordinates


def generate_drone_coordinates_circular(center, radius_meters, num_samples, max_speed=10):
    """
    Generate discrete drone coordinates spinning around a specific point on Earth.

    Parameters:
    - center: Tuple (latitude, longitude) representing the center coordinates in degrees.
    - radius_meters: Radius of the circular path in meters.
    - num_samples: Number of discrete samples to generate.
    - max_speed: Maximum speed of the drone in meters per second.

    Returns:
    List of tuples representing drone coordinates at different time intervals.
    Each tuple is in the format (latitude, longitude, speed) in degrees.
    """
    lat_center, lon_center = center
    coordinates = []

    # Calculate the angular speed in radians per timestep
    circumference = 2 * math.pi * radius_meters  # Circunferência do círculo em metros
    angular_speed = max_speed / radius_meters  # Velocidade angular em radianos por segundo

    for i in range(num_samples):
        angle_radians = angular_speed * i
        lat = lat_center + (radius_meters / earth_radius) * (180 / math.pi) * math.cos(angle_radians)
        lon = lon_center + (radius_meters / earth_radius) * (180 / math.pi) / math.cos(math.radians(lat_center)) * math.sin(angle_radians)

        if i > 0:
            speed = haversine_distance(coordinates[-1][0], coordinates[-1][1], lat, lon)
        else:
            speed = 0  # Inicialmente a velocidade é zero

        coordinates.append((lat, lon, speed))

    return coordinates

def generate_tractor_pattern(start_point, width_between_tracks, max_length, max_turns, orientation, num_samples, max_speed):
    """
    Gera coordenadas para um padrão de mobilidade de trator.

    Parâmetros:
    - start_point (tuple): Coordenadas iniciais (latitude, longitude).
    - width_between_tracks (float): Distância entre cada trilha em metros.
    - max_length (float): Comprimento máximo de cada trilha em metros.
    - max_turns (int): Número máximo de mudanças de direção antes de inverter a direção.
    - orientation (str): 'horizontal' para movimento paralelo ao equador, 'vertical' para movimento meridional.
    - num_samples (int): Número de amostras a serem geradas.
    - max_speed (float): Velocidade máxima do drone em metros por segundo.

    Retorna:
    - Lista de tuplas: Lista de coordenadas (latitude, longitude, velocidade) para o padrão de trator.
    """
    if num_samples <= 0:
        raise ValueError("num_samples deve ser maior que 0")
    if max_turns <= 0:
        raise ValueError("max_turns deve ser maior que 0")
    if orientation not in ['horizontal', 'vertical']:
        raise ValueError("orientation deve ser 'horizontal' ou 'vertical'")

    coordinates = []
    lat, lon = start_point
    current_direction_main = 1  # 1 para frente, -1 para trás
    current_direction_aux = 1
    distance_per_sample = max_speed  # Distância coberta por amostra
    turns = 0
    distance_covered = 0  # Distância percorrida na direção atual

    for i in range(num_samples):
        if i > 0:
            prev_lat, prev_lon, _ = coordinates[-1]
            speed = haversine_distance(prev_lat, prev_lon, lat, lon)  # Distância percorrida em 1 segundo, que é a velocidade
        else:
            speed = 0  # Inicialmente a velocidade é zero

        coordinates.append((lat, lon, speed))

        distance_covered += distance_per_sample
        if distance_covered >= max_length:
            # Mudar de direção e mover para a próxima trilha
            current_direction_main *= -1
            turns += 1
            distance_covered = 0
            if turns >= max_turns:
                # Inverter a direção do movimento principal
                current_direction_aux *= -1
                turns = 0
            # Mover para a próxima linha de latitude (norte ou sul) ou longitude (leste ou oeste)
            distance_to_move = width_between_tracks
            while distance_to_move > 0:
                move_step = min(distance_to_move, distance_per_sample)
                if orientation == 'horizontal':
                    lat += (move_step / earth_radius) * current_direction_aux * (180 / math.pi)
                else:
                    lon += (move_step / earth_radius) * current_direction_aux * (180 / math.pi) / math.cos(math.radians(lat))
                distance_to_move -= move_step
                coordinates.append((lat, lon, max_speed))
        else:
            # Continuar na mesma direção
            if orientation == 'horizontal':
                lon += (distance_per_sample * current_direction_main) / (earth_radius * math.cos(math.radians(lat))) * (180 / math.pi)
            else:
                lat += (distance_per_sample * current_direction_main) / earth_radius * (180 / math.pi)

    return coordinates


def generate_square_pattern(center_point, side_length, angle_degrees, num_samples, max_speed):
    """
    Gera coordenadas para um padrão de mobilidade quadrada.

    Parâmetros:
    - center_point (tuple): Coordenadas centrais (latitude, longitude).
    - side_length (float): Comprimento de cada lado do quadrado em metros.
    - angle_degrees (float): Ângulo do quadrado em relação ao eixo em graus.
    - num_samples (int): Número de amostras a serem geradas.
    - max_speed (float): Velocidade máxima do drone em metros por segundo.

    Retorna:
    - Lista de tuplas: Lista de coordenadas (latitude, longitude, velocidade) para o padrão de mobilidade quadrada.
    """
    if num_samples <= 0:
        raise ValueError("num_samples deve ser maior que 0")

    coordinates = []
    lat, lon = center_point
    distance_per_sample = max_speed  # Distância coberta por amostra
    distance_covered = 0  # Distância percorrida na direção atual
    current_side = 0  # Lado atual do quadrado (0: norte, 1: leste, 2: sul, 3: oeste)

    # Ângulo de rotação do quadrado
    angle_radians = math.radians(angle_degrees)
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)

    def rotate_point(lat, lon, center_lat, center_lon, cos_angle, sin_angle):
        """
        Rotaciona um ponto em torno de um centro dado um ângulo.
        """
        lat_m = (lat - center_lat) * earth_radius * (math.pi / 180)
        lon_m = (lon - center_lon) * earth_radius * math.cos(math.radians(center_lat)) * (math.pi / 180)

        rotated_lat_m = lat_m * cos_angle - lon_m * sin_angle
        rotated_lon_m = lat_m * sin_angle + lon_m * cos_angle

        rotated_lat = rotated_lat_m / (earth_radius * (math.pi / 180)) + center_lat
        rotated_lon = rotated_lon_m / (earth_radius * math.cos(math.radians(center_lat)) * (math.pi / 180)) + center_lon

        return rotated_lat, rotated_lon

    def move(lat, lon, distance, angle):
        """
        Move um ponto (lat, lon) uma certa distância em metros em uma direção especificada por um ângulo em radianos.
        """
        delta_lat = distance * math.cos(angle) / earth_radius * (180 / math.pi)
        delta_lon = distance * math.sin(angle) / (earth_radius * math.cos(math.radians(lat))) * (180 / math.pi)
        return lat + delta_lat, lon + delta_lon

    # Ângulos base para os quatro lados do quadrado antes da rotação
    base_angles = [0, 90, 180, 270]

    for i in range(num_samples):
        if i > 0:
            prev_lat, prev_lon, _ = coordinates[-1]
            speed = haversine_distance(prev_lat, prev_lon, lat, lon)
        else:
            speed = 0

        coordinates.append((lat, lon, speed))

        distance_covered += distance_per_sample
        if distance_covered >= side_length:
            current_side = (current_side + 1) % 4
            distance_covered = 0

        current_angle = math.radians(base_angles[current_side])
        total_angle = current_angle + angle_radians

        lat, lon = move(lat, lon, distance_per_sample, total_angle)

    return coordinates


def generate_drone_coordinates_static(point, num_samples):
    """
    Generate discrete drone coordinates spinning around a specific point on Earth.

    Parameters:
    - center: Tuple (latitude, longitude) representing the center coordinates in degrees.
    - radius_meters: Radius of the circular path in meters.
    - num_samples: Number of discrete samples to generate.
    - max_speed: Maximum speed of the drone in meters per second.

    Returns:
    List of tuples representing drone coordinates at different time intervals.
    Each tuple is in the format (latitude, longitude, speed) in degrees.
    """
    lat_center, lon_center = point
    coordinates = []


    for i in range(num_samples):
        coordinates.append((lat_center, lon_center, 0))

    return coordinates


def create_drone_static_point(timesteps, drone_id,point):
    drone_coordinates = generate_drone_coordinates_static(point, timesteps)
    drone = Vehicle(drone_id, "VANT")

    for time in range(timesteps):
        x_current, y_current, speed = drone_coordinates[time]
        
        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2), "0", "0", "0")

    return drone

def create_drone_following_object(timesteps, drone_id, vehicle, offset_distance, max_speed):
    vehicle_data = [vehicle.get_timestep_dict(i) for i in range(timesteps + 1)]
    coordinates = [(data['x'], data['y']) if data else (0, 0) for data in vehicle_data]

    drone_coordinates = generate_drone_coordinates(coordinates, offset_distance,max_speed)
    drone = Vehicle(drone_id, "VANT")

    first = True

    for time in range(timesteps + 1):
        x_current, y_current, speed = drone_coordinates[time]
        
        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2)  , "0", "0", "0")
            if first == True:
                for timeIn in range(time):
                    drone.add_timestep(timeIn, x_current, y_current, "0", round(speed, 2)  , "0", "0", "0")
                first = False

         

    return drone

def create_drone_circular_point(timesteps, drone_id, center, radius_meters, max_speed):
    drone_coordinates = generate_drone_coordinates_circular(center, radius_meters, timesteps, max_speed)
    drone = Vehicle(drone_id, "VANT")

    for time in range(timesteps):
        x_current, y_current, speed = drone_coordinates[time]
        
        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2), "0", "0", "0")

    return drone
    
def create_drone_tractor_pattern(timesteps, drone_id, start_point, width_between_tracks, max_length, max_turns, orientation, max_speed):
    drone_coordinates = generate_tractor_pattern(start_point, width_between_tracks, max_length, max_turns, orientation, timesteps, max_speed)
    drone = Vehicle(drone_id, "VANT")

    for time in range(timesteps):
        x_current, y_current, speed = drone_coordinates[time]
        
        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2), "0", "0", "0")

    return drone

def create_drone_square_pattern(timesteps, drone_id, center_point, side_length, angle_degrees, max_speed):
    drone_coordinates = generate_square_pattern(center_point, side_length, angle_degrees, timesteps, max_speed)
    drone = Vehicle(drone_id, "VANT")

    for time in range(timesteps):
        x_current, y_current, speed = drone_coordinates[time]
        
        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2), "0", "0", "0")

    return drone