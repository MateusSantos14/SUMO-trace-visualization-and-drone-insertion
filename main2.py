#Nova Simulação
from Simulation import Simulation
from Tools import FilterTimesteps
from conversiontometers import convert_coordinates

simulacao = Simulation("Traces/osmWithStop.xml")

simulacao.create_drone_following("f_0.0",4)
#simulacao.create_drone_circular((-38.576, -3.74204395),50)
#simulacao.create_drone_tractor((-38.576, -3.74204395),40,200,3,"horizontal")
simulacao.create_drone_square((-38.577, -3.74204395),100,0)
simulacao.create_drone_square((-38.577, -3.74204395),100,45)

#simulacao.print_all_vehicle_info("drone1")
simulacao.export_timesteps_to_xml("outputns3a.xml")

convert_coordinates('outputns3a.xml', 'outputns3conva.xml')

simulacao.export_to_video("simulation_video5")

#test trace exporter
#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\outputns3conva.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\mobility.tcl