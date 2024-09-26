from Simulation import Simulation
from conversiontometers import convert_coordinates

simulacao = Simulation("scenario1.xml")

simulacao.create_drone_static((100,100))
simulacao.create_drone_static((100,200))

simulacao.export_timesteps_to_xml("scenario1.xml")


simulacao = Simulation("scenario2.xml")

simulacao.create_drone_static((100,100))
simulacao.create_drone_static((100,100))

simulacao.export_timesteps_to_xml("scenario2.xml")
#simulacao.export_to_video("simulation_video3",((40.740,-73.990),(40.750,-73.980)))

#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\mahattanDrone.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\mahattanDrone.tcl