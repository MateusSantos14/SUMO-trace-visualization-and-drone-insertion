from Simulation import Simulation
from conversiontometers import convert_coordinates

simulacao = Simulation("manhattan.xml")

simulacao.create_drone_following("0", 5)

simulacao.export_timesteps_to_xml("mahattanDronea.xml")
convert_coordinates("mahattanDronea.xml","mahattanDroneab.xml")

#simulacao.export_to_video("simulation_video3",((40.740,-73.990),(40.750,-73.980)))

#simulacao.export_to_video("simulation_video3")

#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\mahattanDrone.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\mahattanDrone.tcl