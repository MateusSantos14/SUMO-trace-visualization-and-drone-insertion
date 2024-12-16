import xml.etree.ElementTree as ET
from xml.dom import minidom

from Vehicle import *
from videomaker import generate_video_with_vector_coordinates_image
from creating_drones import create_drone_following_object,create_drone_circular_point,create_drone_tractor_pattern,create_drone_square_pattern,create_drone_static_point,create_drone_angular_pattern

class Simulation:
    def __init__(self, trace_path):
        # Vars
        self.vehicleList = {} #List with all vehicles
        self.typeList = {}
        self.typeList["VANT"] = "VANT"
        self.timestep_total = 0
        self.trace_path = trace_path
        self.droneNumber = 0
        self.read_xml(trace_path)
        
    def read_xml(self,trace_path):
        # Load and parse the XML file
        outputxml = ET.parse(trace_path)
        timestepList = outputxml.getroot()

        # Print the root element tag
        for timestep in timestepList:
            timeInstant = timestep.attrib['time']
            self.timestep_total = int(float(timeInstant))
            for timestepVehicleData in timestep:
                if(timestepVehicleData.tag == "vehicle"):
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

                    #Add to vehicleList dictionary
                    if vehicleId not in self.vehicleList.keys():
                        self.vehicleList[vehicleId] = Vehicle(vehicleId,vehicleType)
                        if vehicleType not in self.typeList:
                            self.typeList[vehicleType] = vehicleType

                    #Add timesteps
                    self.vehicleList[vehicleId].add_timestep(timeInstant, vehicleX, vehicleY, vehicleAngle, vehicleSpeed, vehiclePos, vehicleLane, vehicleSlope)
    

    def getVehicleById(self,id):
        if id in self.vehicleList.keys():
            return self.vehicleList[id]
        else:
            raise ValueError("ID not found in simulation.")
        
    def export_to_video(self,video_directory,limits_map = 0,only_vants=0):
        video_directory+=".mp4"
        names = list(self.typeList.keys())
        vector_coordinates = [[] for i in names]
        for vehicle_id in self.vehicleList.keys():
            coordinates = []
            vehicle_object = self.vehicleList[vehicle_id]
            for i in range(int(float(self.timestep_total)+1)):
                timestep = vehicle_object.get_timestep(i)
                if timestep == None:
                    coordinates.append((0,0))
                else:
                    coordinates.append((timestep.x(),timestep.y()))
            index_in_vector_coordinates = names.index(vehicle_object.type())
            vector_coordinates[index_in_vector_coordinates].append(coordinates)
        names = list(self.typeList.values())#MUDEI PARA TESTE
        
        generate_video_with_vector_coordinates_image(vector_coordinates,video_directory,names,limits_map,only_vants)


    def get_timestep_total(self):
        return self.timestep_total

    def export_timesteps_to_xml(self, new_xml_path):
        # Load and parse the original XML file
        tree = ET.parse(self.trace_path)
        root = tree.getroot()

        # Iterate over each timestep in the original XML
        for timestep in root.findall('timestep'):
            time = timestep.attrib['time']

            # Remove all vehicle elements from the current timestep
            for vehicle in timestep.findall('vehicle'):
                timestep.remove(vehicle)
            
            # Now, add back vehicles from the simulation's current state
            if int(float(time)) <= self.timestep_total:
                for vehicle_id, vehicle_obj in self.vehicleList.items():
                    if vehicle_obj.is_present(int(float(time))):
                        timestep_vehicle = vehicle_obj.get_timestep(int(float(time)))
                        ET.SubElement(timestep, 'vehicle', {
                            'id': vehicle_obj.id(),
                            'x': str(timestep_vehicle.x()),
                            'y': str(timestep_vehicle.y()),
                            'angle': str(timestep_vehicle.angle()),
                            'type': vehicle_obj.type(),
                            'speed': str(timestep_vehicle.speed()),
                            'pos': str(timestep_vehicle.pos()),
                            'lane': timestep_vehicle.lane(),
                            'slope': str(timestep_vehicle.slope())
                        })

        # Write the modified XML tree to a new file
        tree.write(new_xml_path, encoding='utf-8', xml_declaration=True)
    
    def create_drone_angular(self, start_point, max_length, max_turns=3, angle_alpha=30,max_speed=10):

        self.droneNumber+=1
        
        drone = create_drone_angular_pattern(self.timestep_total, f"drone{self.droneNumber}", start_point, max_length, max_turns, angle_alpha, max_speed)

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_static(self,point):
        self.droneNumber+=1
        
        drone = create_drone_static_point(self.timestep_total,f"drone{self.droneNumber}",point)

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_following(self,vehicle_id,offset_distance,max_speed=10):
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]

        self.droneNumber+=1
        
        drone = create_drone_following_object(self.timestep_total,f"drone{self.droneNumber}",vehicle,offset_distance,max_speed=max_speed)

        self.vehicleList[f"drone{self.droneNumber}"] = drone
    
    def create_drone_circular(self, center, radius_meters, max_speed = 10):

        self.droneNumber+=1
        
        drone = create_drone_circular_point(self.timestep_total, f"drone{self.droneNumber}", center, radius_meters, max_speed)

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_tractor(self, start_point, width_between_tracks, max_length, max_turns, orientation='horizontal', max_speed = 10):

        self.droneNumber+=1
        
        drone = create_drone_tractor_pattern(self.timestep_total, f"drone{self.droneNumber}", start_point, width_between_tracks, max_length, max_turns, orientation, max_speed)

        self.vehicleList[f"drone{self.droneNumber}"] = drone
    
    def create_drone_square(self, center_point, side_length, angle_degrees, max_speed = 10):

        self.droneNumber+=1
        
        drone = create_drone_square_pattern(self.timestep_total, f"drone{self.droneNumber}", center_point, side_length, angle_degrees, max_speed)

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    #Add your own vehicle
    def addVehicle(self,vehicle):
        if vehicle.id() in self.vehicleList.keys():
            raise ValueError("ID already exists.")
        else:
            self.vehicleList[vehicle.id()]
            if vehicle.type() not in self.typeList:
                self.typeList[vehicle.type()] = vehicle.type()

    def removeVehicle(self,vehicleId):
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
 

    #Debug tools
    def print_all_vehicle_info(self,vehicle_id):
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]
        for i in range(self.timestep_total+1):
            timestep = vehicle.get_timestep_dict(i)
            if timestep != None:
                print(timestep)

    def vector_with_all_coordinates(self):
        names = list(self.typeList.keys())
        vector_coordinates = [[] for i in names]
        for vehicle_id in self.vehicleList.keys():
            coordinates = []
            vehicle_object = self.vehicleList[vehicle_id]
            for i in range(int(float(self.timestep_total)+1)):
                timestep = vehicle_object.get_timestep(i)
                if timestep == None:
                    coordinates.append((0,0))
                else:
                    coordinates.append((timestep.x(),timestep.y()))
            index_in_vector_coordinates = names.index(vehicle_object.type())
            vector_coordinates[index_in_vector_coordinates].append(coordinates)
        return vector_coordinates

        
        
        





