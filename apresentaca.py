from Simulation import Simulation
from Tools import FilterTimesteps
from conversiontometers import convert_coordinates

# Inicializa a simulação
simulacao = Simulation("manhattan.xml")

# Coordenadas centrais e limites do cenário
center_point = (-73.983228, 40.744475)  # Ponto central escolhido
boundary_point = (-73.970122, 40.735626)  # Um dos limites como exemplo

# Criação de drones com diferentes padrões de mobilidade

# Drone estático
simulacao.create_drone_static(center_point)

# Drone seguindo um veículo (Exemplo: "vehicle1")
vehicle_id = "101"
offset_distance = 15  # Distância de 15 metros do veículo
simulacao.create_drone_following(vehicle_id, offset_distance)

# Drone com padrão circular
radius_meters = 50  # Raio de 50 metros
simulacao.create_drone_circular((-73.988003,40.742247), radius_meters)

# Drone com padrão tractor
start_point = (-73.994808, 40.753080)  # Ponto inicial
width_between_tracks = 20  # Distância entre trilhas de 20 metros
max_length = 100  # Comprimento máximo de 100 metros
max_turns = 5  # Máximo de 5 curvas
simulacao.create_drone_tractor((-73.978712,40.745146), width_between_tracks, max_length, max_turns)

for i in range(100,200):
    simulacao.removeVehicle(str(i))

simulacao.changeLegend("myType","car")

# Exporta o cenário para vídeo
simulacao.export_to_video("apresentacao")