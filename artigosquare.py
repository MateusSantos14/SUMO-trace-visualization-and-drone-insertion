from Simulation import Simulation
from Tools import FilterTimesteps
from conversiontometers import convert_coordinates

simulacao = Simulation("manhattanmedium.xml")

simulacao.create_drone_tractor((-73.983213,40.744658),80,80,1)

simulacao.print_all_vehicle_info("drone1")

simulacao.export_timesteps_to_xml("mahattanDrone.xml")

convert_coordinates("mahattanDrone.xml","urban-medium-square.xml")

simulacao.export_to_video("square_artigo")

#test trace exporter
#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\urban-medium-static.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\urban-medium-static.tcl

#Test Manhattan Scenario
#sumo -c C:\Users\Pichau\Desktop\manhattan_cenario_SBRC-master\denso\denso.sumocfg --fcd-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattandenso.xml --fcd-output.geo true
