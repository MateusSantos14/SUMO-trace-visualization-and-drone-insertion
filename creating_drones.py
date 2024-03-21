import math
from Vehicle import Vehicle

earth_radius = 6371000 #Meters

def calculate_angle(p1, p2):
    # Distância dos dois pontos
    distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    # Confere a distância e se for pequena usa o mesmo angulo
    if distance < 1e-6:
        return None

    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def generate_drone_coordinates(vehicle_coordinates, offset_distance,  smoothing_factor=0.4):
    """
    Generate drone coordinates based on the vehicle coordinates and offset distance.

    Parameters:
    - vehicle_coordinates (list of tuples): List of (x, y) coordinates for the vehicle path.
    - offset_distance (float): Distance between the vehicle and the drone in meters.
    - max_speed (float): Maximum speed of the drone in meters per second.
    - smoothing_factor (float): Smoothing factor for gentle movement. Value between 0 and 1.

    Returns:
    - list of tuples: List of (x, y) coordinates for the drone path.
    """
    
    offset_distance = offset_distance*360/earth_radius

    drone_coordinates = []

    first_non_zero_coordinate = False

    for i, vehicle_position in enumerate(vehicle_coordinates):
        if vehicle_position != (0, 0) and first_non_zero_coordinate == False:
            first_non_zero_coordinate = True
            drone_coordinates.append((vehicle_position[0], vehicle_position[1]))

        #if not first_non_zero_coordinate:
        if vehicle_position == (0, 0):
            drone_coordinates.append((0, 0))
            continue

        if i < len(vehicle_coordinates) - 1:
            angle = calculate_angle(vehicle_coordinates[i], vehicle_coordinates[i + 1])
        else:
            angle = calculate_angle(vehicle_coordinates[i - 1], vehicle_coordinates[i])

        if angle is None and i > 0:
            drone_coordinates.append(drone_coordinates[-1])
        else:
            desired_x = vehicle_position[0] - offset_distance * math.cos(angle)
            desired_y = vehicle_position[1] - offset_distance * math.sin(angle)

            current_x, current_y = drone_coordinates[-1]
            smoothed_x = current_x + smoothing_factor * (desired_x - current_x)
            smoothed_y = current_y + smoothing_factor * (desired_y - current_y)

            drone_coordinates.append((smoothed_x, smoothed_y))

    return drone_coordinates

def generate_drone_coordinates_circular(center, radius_meters, angular_speed, num_samples):
    """
    Generate discrete drone coordinates spinning around a specific point on Earth.

    Parameters:
    - center: Tuple (latitude, longitude) representing the center coordinates in degrees.
    - radius_degrees: Radius of the circular path in meters.
    - angular_speed: Angular speed in degrees per sample.
    - num_samples: Number of discrete samples to generate.

    Returns:
    List of tuples representing drone coordinates at different time intervals.
    Each tuple is in the format (latitude, longitude) in degrees.
    """
    lat_center, lon_center = center
    coordinates = []

    radius_degrees = radius_meters*360/earth_radius

    for i in range(num_samples):
        # Calculate current angle based on the sample index and angular speed
        angle_degrees = angular_speed * i

        # Convert angle from degrees to radians
        angle_radians = math.radians(angle_degrees)

        # Calculate drone coordinates in polar coordinates
        lat = lat_center + radius_degrees * math.cos(angle_radians)
        lon = lon_center + radius_degrees * math.sin(angle_radians) / math.cos(math.radians(lat_center))

        coordinates.append((lat, lon))

    return coordinates

def create_drone_following_object(timesteps,drone_id,vehicle,offset_distance):
    vehicle_data = []
    for i in range(timesteps+1):
        vehicle_data.append(vehicle.get_timestep_dict(i))
    coordinates = []
    for data in vehicle_data:
        if data == None:
            coordinates.append((0,0))
        else:    
            coordinates.append((data['x'], data['y']))
    drone_coordinates = generate_drone_coordinates(coordinates,offset_distance)
    drone = Vehicle(drone_id,"VANT")
    
    for time in range(timesteps+1):
        if drone_coordinates[time][0] != 0 or drone_coordinates[time][1] != 0:
            speed = 0
            if time != timesteps:#Check if it is the last entry.
                if drone_coordinates[time-1][0] != 0 or drone_coordinates[time-1][1] != 0:#Check if there is a next entry.
                    speed_angle = math.sqrt((drone_coordinates[time][0]-drone_coordinates[time-1][0])**2+(drone_coordinates[time][1]-drone_coordinates[time-1][1])**2)
                    speed = 2*math.pi*(speed_angle/360)*earth_radius
                    speed = f"{speed}"
            drone.add_timestep(time,drone_coordinates[time][0],drone_coordinates[time][1],"0",speed,"0","0","0")
    return drone


def create_drone_circular_point(timesteps, drone_id, center, radius_meters, angular_speed):
    drone_coordinates = generate_drone_coordinates_circular(center, radius_meters, angular_speed, timesteps)
    drone = Vehicle(drone_id,"VANT")
    
    for time in range(timesteps):
        if drone_coordinates[time][0] != 0 or drone_coordinates[time][1] != 0:
            speed = 0
            if time != timesteps:#Check if it is the last entry.
                if drone_coordinates[time-1][0] != 0 or drone_coordinates[time-1][1] != 0:#Check if there is a next entry.
                    speed_angle = math.sqrt((drone_coordinates[time][0]-drone_coordinates[time-1][0])**2+(drone_coordinates[time][1]-drone_coordinates[time-1][1])**2)
                    speed = 2*math.pi*(speed_angle/360)*earth_radius
                    speed = f"{speed}"
            drone.add_timestep(time,drone_coordinates[time][0],drone_coordinates[time][1],"0",speed,"0","0","0")
    return drone
    
