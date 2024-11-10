from Simulation import Simulation
from Tools import FilterTimesteps
from conversiontometers import convert_coordinates

simulacao = Simulation("manhattandenso2.xml")

simulacao.create_drone_static((-73.983228, 40.744475))

simulacao.print_all_vehicle_info("drone1")

simulacao.export_timesteps_to_xml("mahattanDrone2.xml")

convert_coordinates("mahattanDrone2.xml","urban-high.xml")

#simulacao.export_to_video("simulation_video3")


#test trace exporter
#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\urban-high.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\urban-high.tcl

#Test Manhattan Scenario
#sumo -c C:\Users\Pichau\Desktop\manhattan_cenario_SBRC-master\denso\denso.sumocfg --fcd-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattandenso.xml --fcd-output.geo true
