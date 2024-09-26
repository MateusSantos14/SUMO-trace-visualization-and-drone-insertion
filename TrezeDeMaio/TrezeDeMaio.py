#Nova Simulação
from Simulation import Simulation
from conversiontometers import convert_coordinates

simulacao = Simulation("TrezeDeMaion.xml")
simulacao.create_drone_square((-38.538973, -3.741977),100,0)
simulacao.export_timesteps_to_xml("TrezeDeMaioV.xml")
convert_coordinates('TrezeDeMaioV.xml', 'TrezeDeMaioV.xml')

simulacao.export_to_video("simulation_video8")
simulacao.export_to_video("simulation_video8",only_vants=1)



#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\TrezeDeMaioV.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\TrezeDeMaioV.tcl