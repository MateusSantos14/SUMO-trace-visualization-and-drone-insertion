class Vehicle:
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
    
    

