from Simulation import Simulation


simulacao = Simulation("manhattan.xml")


distance = 40
angles = [180,90,0,270]

distance_list = []
angle_list = []

for i in range(4):
    distance_list.append(distance)
    angle_list.append(angles[i%4])

simulacao.create_drone_generic((-73.986478,40.744406),distance_list,angle_list)

print("aaa")
print(len(simulacao.get_vehicle_dict("drone1")))

#simulacao.export_to_video("feature")


