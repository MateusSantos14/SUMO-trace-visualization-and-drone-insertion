class Vehicle:
    """
    The Vehicle class is designed to store and manage vehicle trace information.

    Attributes:
    - _id (str): The unique identifier for the vehicle.
    - _type (str): The type of the vehicle.
    - timesteps (dict): A dictionary storing Timestep objects, indexed by time (as integers).

    Methods:
    - __init__(self, id: str, type: str):
    Initializes a new Vehicle instance with the specified ID and type.
    
    - add_timestep(self, time: str, x: str, y: str, angle: str, speed: str, pos: str, lane: str, slope: str):
    Adds a new timestep to the vehicle's history, converting string inputs into appropriate data types where necessary.
    
    - get_timestep(self, time: int) -> Timestep | None:
    Retrieves the Timestep object for a given time if it exists; otherwise, returns None.
    
    - get_timestep_dict(self, time: int) -> dict | None:
    Returns a dictionary representation of a Timestep for a given time if it exists; otherwise, returns None.
    
    - print_timestep(self, time: int):
    Prints the dictionary representation of a Timestep for a given time if it exists.
    
    - is_present(self, time: int) -> bool:
    Checks if there's a Timestep for a given time, returning True if present; otherwise, False.
    
    - id(self) -> str:
    Returns the vehicle's ID.
    
    - type(self) -> str:
    Returns the vehicle's type.
    """
    def __init__(self,id,type):
        self._id = id
        self._type = type
        self.timesteps = {} 
    
    def add_timestep(self, time, x, y, angle, speed, pos, lane, slope):
        time = int(float(time))
        timestep = Timestep(time,float(x),float(y),float(angle),float(speed),float(pos),lane,float(slope))
        self.timesteps[timestep.time()] = timestep  # Adiciona um timestep indexado pelo tempo

    def get_timestep(self, time):
        if time in self.timesteps.keys():
            return self.timesteps.get(time) # Retorna o timestep para um determinado momento, se existir
        else:
            return None
    
    def get_timestep_dict(self,time):
        if time in self.timesteps.keys():
            timestep = self.timesteps.get(time)
            timestepdata = {"id":self.id(),"x":timestep.x(),"y":timestep.y(),"angle":timestep.angle(),"speed":timestep.speed(),"pos":timestep.pos(),"lane":timestep.lane(),"slope":timestep.slope()}
            return timestepdata
        else:
            return None
        
    def print_timestep(self,time):
        if time in self.timesteps.keys():
            timestep = self.timesteps[time]
            print(timestep.dict())

    def is_present(self,time):
        if time in self.timesteps.keys():
            return True
        else:
            return False

    def id(self):
        return self._id
    
    def type(self):
        return self._type


class Timestep:
    """
    Timestep Class:

    Encapsulates the state of a vehicle at a specific moment in time, detailing its position, orientation, and motion attributes.

    Attributes:
    - _time (int): Time point of the timestep.
    - _x (float): X-coordinate of the vehicle's position.
    - _y (float): Y-coordinate of the vehicle's position.
    - _angle (float): Vehicle's orientation angle.
    - _speed (float): Vehicle's speed.
    - _pos (float): Position indicator, detailed meaning depends on the application context.
    - _lane (str): Lane of the vehicle, interpretation depends on the application.
    - _slope (float): Road slope or vehicle inclination angle.

    Methods:
    - __init__(self, time, x, y, angle, speed, pos, lane, slope):
    Initializes a Timestep with position, orientation, and motion details.
    
    - time(self) -> float:
    Returns the time point of this timestep.
    
    - x(self) -> float:
    Returns the x-coordinate of the vehicle's position.
    
    - y(self) -> float:
    Returns the y-coordinate of the vehicle's position.
    
    - angle(self) -> float:
    Returns the vehicle's orientation angle.
    
    - speed(self) -> float:
    Returns the vehicle's speed.
    
    - pos(self):
    Returns a position indicator of the vehicle.
    
    - lane(self):
    Returns the lane of the vehicle.
    
    - slope(self) -> float:
    Returns the slope of the road or vehicle inclination.
    """
    def __init__(self,time,x,y,angle,speed,pos,lane,slope):
            self._time = time
            self._x = x
            self._y = y
            self._angle = angle
            self._speed = speed
            self._pos = pos
            self._lane = lane
            self._slope = slope

    def time(self):
        return self._time
    def x(self):
        return self._x
    def y(self):
        return self._y
    def angle(self):
        return self._angle
    def speed(self):
        return self._speed
    def pos(self):
        return self._pos
    def lane(self):
        return self._lane
    def slope(self):
        return self._slope
    
    

