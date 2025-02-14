import xml.etree.ElementTree as ET
from xml.dom import minidom

import math
from src.Vehicle import *
from src.videomaker import generate_video_with_vector_coordinates_image
from src.creating_drones import (
    create_drone_following_object,
    create_drone_tractor_pattern,
    create_drone_static_point,
    create_drone_angular_pattern,
    create_drone_generic_pattern,
    meters_to_geo,
)
from src.utils.offSetTool import read_and_offset_trace as offset
from src.utils.conversionMeters import convert_coordinates

class Simulation:
    def __init__(self, trace_path):
        self.vehicleList = {}  # List with all vehicles
        self.typeList = {}
        self.typeList["VANT"] = "UAV"
        self.timestep_total = 0
        self.trace_path = trace_path
        self.droneNumber = 0
        self.read_xml(trace_path)

    def read_xml(self, trace_path):
        outputxml = ET.parse(trace_path)
        timestepList = outputxml.getroot()
        for timestep in timestepList:
            timeInstant = timestep.attrib["time"]
            self.timestep_total = int(float(timeInstant))
            for timestepVehicleData in timestep:
                if timestepVehicleData.tag == "vehicle":
                    vehicleData = timestepVehicleData.attrib
                    vehicleId = vehicleData["id"]
                    vehicleX = vehicleData["x"]
                    vehicleY = vehicleData["y"]
                    vehicleAngle = vehicleData["angle"]
                    vehicleType = vehicleData["type"]
                    vehicleSpeed = vehicleData["speed"]
                    vehiclePos = vehicleData["pos"]
                    vehicleLane = vehicleData["lane"]
                    vehicleSlope = vehicleData["slope"]
                    if vehicleId not in self.vehicleList.keys():
                        self.vehicleList[vehicleId] = Vehicle(vehicleId, vehicleType)
                        if vehicleType not in self.typeList:
                            self.typeList[vehicleType] = vehicleType
                    self.vehicleList[vehicleId].add_timestep(
                        str(float(timeInstant)+1),
                        vehicleX,
                        vehicleY,
                        vehicleAngle,
                        vehicleSpeed,
                        vehiclePos,
                        vehicleLane,
                        vehicleSlope,
                    )
        self.timestep_total+=1

    def getVehicleById(self, id):
        if id in self.vehicleList.keys():
            return self.vehicleList[id]
        else:
            raise ValueError("ID not found in simulation.")

    def export_to_video(self, video_directory, limits_map=0, only_vants=0):
        video_directory += ".mp4"
        names = list(self.typeList.keys())
        vector_coordinates = [[] for i in names]
        for vehicle_id in self.vehicleList.keys():
            coordinates = []
            vehicle_object = self.vehicleList[vehicle_id]
            for i in range(int(float(self.timestep_total) + 1)):
                timestep = vehicle_object.get_timestep(i)
                if timestep == None:
                    coordinates.append((0, 0))
                else:
                    coordinates.append((timestep.x(), timestep.y()))
            index_in_vector_coordinates = names.index(vehicle_object.type())
            vector_coordinates[index_in_vector_coordinates].append(coordinates)
        names = list(self.typeList.values())  # MUDEI PARA TESTE

        generate_video_with_vector_coordinates_image(
            vector_coordinates, video_directory, names, limits_map, only_vants
        )

    def get_timestep_total(self):
        return self.timestep_total

    def export_timesteps_to_xml(self, new_xml_path,geo = 1):
        tree = ET.parse(self.trace_path)
        root = tree.getroot()

        for timestep in root.findall("timestep"):
            time = timestep.attrib["time"]
            for vehicle in timestep.findall("vehicle"):
                timestep.remove(vehicle)

            if int(float(time)) <= self.timestep_total:
                for vehicle_id, vehicle_obj in self.vehicleList.items():
                    if vehicle_obj.is_present(int(float(time))):
                        timestep_vehicle = vehicle_obj.get_timestep(int(float(time)))
                        ET.SubElement(
                            timestep,
                            "vehicle",
                            {
                                "id": vehicle_obj.id(),
                                "x": str(timestep_vehicle.x()),
                                "y": str(timestep_vehicle.y()),
                                "angle": str(timestep_vehicle.angle()),
                                "type": vehicle_obj.type(),
                                "speed": str(timestep_vehicle.speed()),
                                "pos": str(timestep_vehicle.pos()),
                                "lane": timestep_vehicle.lane(),
                                "slope": str(timestep_vehicle.slope()),
                            },
                        )
        tree.write(new_xml_path, encoding="utf-8", xml_declaration=True)
        if geo == 0:
            convert_coordinates(new_xml_path,new_xml_path)

    def create_drone_angular(
        self, start_point, max_length, max_turns=3, angle_alpha=30, max_speed=10
    ):
        self.droneNumber += 1

        drone = create_drone_angular_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            max_length,
            max_turns,
            angle_alpha,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_static(self, point):
        self.droneNumber += 1

        drone = create_drone_static_point(
            self.timestep_total, f"drone{self.droneNumber}", point
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_following(self, vehicle_id, offset_distance, max_speed=10):
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]

        self.droneNumber += 1

        drone = create_drone_following_object(
            self.timestep_total,
            f"drone{self.droneNumber}",
            vehicle,
            offset_distance,
            max_speed=max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone
    """
    def create_drone_tractor(
        self,
        start_point,
        width_between_tracks,
        max_length,
        max_turns,
        orientation="horizontal",
        max_speed=10,
    ):
        self.droneNumber += 1

        drone = create_drone_tractor_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            width_between_tracks,
            max_length,
            max_turns,
            orientation,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone
    """
    def create_drone_tractor(
        self,
        start_point,
        width_between_tracks,
        max_length,
        max_turns,
        orientation="horizontal",
        max_speed=10,
    ):
        self.droneNumber += 1
        
        distance_list = []
        angle_list = []
        
        # Initialize base angles based on orientation
        if orientation == "horizontal":
            start_angle = 0  # Move right
        else:  # vertical
            start_angle = 90  # Move up
        distance_list.append(width_between_tracks)
        angle_list.append(start_angle)
        # Create the tractor pattern
        for turn in range(max_turns):
            if turn%2==0:
                angle_list.append(start_angle-90)
                distance_list.append(max_length)
            else:
                angle_list.append(start_angle+90)
                distance_list.append(max_length)
            distance_list.append(width_between_tracks)
            angle_list.append(start_angle)
        angle_list.append(-start_angle)
        distance_list.append(width_between_tracks)
        for turn in range(max_turns):
            angle_list.append(-start_angle)
            distance_list.append(width_between_tracks)
            if turn%2==0:
                angle_list.append(start_angle+90)
                distance_list.append(max_length)
            else:
                angle_list.append(start_angle-90)
                distance_list.append(max_length)
        
        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_list,
            angle_list,
            max_speed,
        )
        
        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_circular(self, center, radius_meters, max_speed=10, start_angle=0):
        self.droneNumber += 1
        omega = max_speed / radius_meters  # Angular velocity in radians per second

        # Calculate the initial position based on the start angle
        start_point = (
            center[0] + meters_to_geo(radius_meters) * math.cos(math.radians(start_angle)),
            center[1] + meters_to_geo(radius_meters) * math.sin(math.radians(start_angle)),
        )

        # Generate the distance and angle lists based on the angular velocity
        distance_list = []
        angle_list = []

        # Number of steps to complete one full circle
        steps_per_circle = int((2 * math.pi) / omega)

        for i in range(steps_per_circle):
            theta_i = math.radians(start_angle) + omega * i  # Current angle in radians
            angle_list.append(math.degrees(theta_i))  # Store angles in degrees
            distance_list.append(max_speed)  # Distance covered in each time step

        print("Start Point:", start_point)
        print("Center Point:", center)
        print("Distance List:", distance_list)
        print("Angle List:", angle_list)

        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_list,
            angle_list,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone


    def create_drone_square(
        self, center_point, side_length, angle_degrees=90, max_speed=10
    ):
        self.droneNumber += 1

        distance_list = []
        angle_list = []

        for i in range(4):
            distance_list.append(side_length)
            angle = angle_degrees - (90 * i)
            if angle < 0:
                angle += 360
            angle_list.append(angle)
        center_direction = ((-3) * angle_degrees) + 315
        if center_direction < 0:
            angle = 360 + (angle % 360)
        start_point = (
            center_point[0]
            - abs(
                meters_to_geo(math.sqrt(2) * side_length / 2)
                * math.cos(math.radians(center_direction))
            ),
            center_point[1]
            - abs(
                meters_to_geo(math.sqrt(2) * side_length / 2)
                * math.sin(math.radians(center_direction))
            ),
        )
        print(start_point)
        print(center_point)
        print(distance_list)
        print(angle_list)
        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_list,
            angle_list,
            max_speed,
        )

        # drone = create_drone_square_pattern(self.timestep_total, f"drone{self.droneNumber}", center_point, side_length, angle_degrees, max_speed)
        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_generic(
        self, start_point, distance_lists, angles_list, max_speed=10
    ):
        self.droneNumber += 1

        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_lists,
            angles_list,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def addVehicle(self, vehicle):
        if vehicle.id() in self.vehicleList.keys():
            raise ValueError("ID already exists.")
        else:
            self.vehicleList[vehicle.id()]
            if vehicle.type() not in self.typeList:
                self.typeList[vehicle.type()] = vehicle.type()

    def removeVehicle(self, vehicleId):
        if vehicleId not in self.vehicleList.keys():
            raise ValueError("ID doesn't exists.")
        else:
            del self.vehicleList[vehicleId]

    def changeLegend(self, oldLegend, newLegend):
        print
        if oldLegend not in self.typeList.keys():
            raise ValueError("Type does not exists")
        else:
            self.typeList[oldLegend] = newLegend

    def print_all_vehicle_info(self, vehicle_id):
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]
        for i in range(self.timestep_total + 1):
            timestep = vehicle.get_timestep_dict(i)
            if timestep != None:
                print(timestep)

    def get_vehicle_dict(self, vehicle_id):
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]
        timesteps = []
        for i in range(self.timestep_total + 1):
            timestep = vehicle.get_timestep_dict(i)
            timesteps.append(timestep)
        return timesteps

    def vector_with_all_coordinates(self):
        names = list(self.typeList.keys())
        vector_coordinates = [[] for i in names]
        for vehicle_id in self.vehicleList.keys():
            coordinates = []
            vehicle_object = self.vehicleList[vehicle_id]
            for i in range(int(float(self.timestep_total) + 1)):
                timestep = vehicle_object.get_timestep(i)
                if timestep == None:
                    coordinates.append((0, 0))
                else:
                    coordinates.append((timestep.x(), timestep.y()))
            index_in_vector_coordinates = names.index(vehicle_object.type())
            vector_coordinates[index_in_vector_coordinates].append(coordinates)
        return vector_coordinates
