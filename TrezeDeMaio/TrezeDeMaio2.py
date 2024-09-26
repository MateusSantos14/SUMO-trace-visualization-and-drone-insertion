#Nova Simulação
from Simulation import Simulation
from conversiontometers import convert_coordinates
#sumo -c C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\2024-07-17-18-20-03\osm.sumocfg --fcd-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\main.py --fcd-output.geo true


simulacao = Simulation("TrezeDeMaio2.xml")
simulacao.create_drone_circular((-38.544265,-3.743507),20)
simulacao.create_drone_circular((-38.541662,-3.743571),15)
#simulacao.create_drone_tractor((-38.537345,-3.742301),40,200,5)
#simulacao.create_drone_tractor((-38.537345,-3.742301),60,200,4,'vertical')
#simulacao.create_drone_square((-38.539821,-3.744079),10,45)
#simulacao.create_drone_square((-38.543249, -3.740142),7,0)


simulacao.export_timesteps_to_xml("TrezeDeMaio2V.xml")
convert_coordinates('TrezeDeMaio2V.xml', 'TrezeDeMaio2V.xml')
simulacao.export_to_video("simulation_video8",((-38.550678,-3.737984),(-38.535821,-3.747698)))
simulacao.export_to_video("simulation_video8a",((-38.550678,-3.737984),(-38.535821,-3.747698)),1)


#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\TrezeDeMaioV.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\TrezeDeMaioV.tcl



"""
create_drone_circular(self, center, radius_meters, max_speed = 10)
create_drone_tractor(self, start_point, width_between_tracks, max_length, max_turns, orientation, max_speed = 10)
create_drone_square(self, center_point, side_length, angle_degrees, max_speed = 10)

"""