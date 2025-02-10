from Simulation import Simulation
from Tools import FilterTimesteps
from conversiontometers import convert_coordinates
import math

simulacao = Simulation("manhattanmedium.xml")

distance = 10
angle_step = distance / 40
angle = 90

distance_list = []
angle_list = []

for i in range(1000):
    distance_list.append(distance)
    angle_list.append(angle + math.degrees(angle * (i + 1)))
    if angle_list[-1] == angle:
        break
simulacao.create_drone_generic((-73.983213, 40.744658), distance_list, angle_list)

# simulacao.create_drone_square((-73.983213,40.744658),80)

# simulacao.create_drone_static((-73.983213,40.744658))


simulacao.export_to_video("featurec")

# test trace exporter
# py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\urban-medium-square.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\urban-medium-square.tcl

# Test Manhattan Scenario
# sumo -c C:\Users\Pichau\Desktop\manhattan_cenario_SBRC-master\denso\denso.sumocfg --fcd-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattandenso.xml --fcd-output.geo true
