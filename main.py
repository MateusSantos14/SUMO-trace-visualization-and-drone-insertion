from Simulation import Simulation
from Tools import FilterTimesteps


simulacao = Simulation("manhattan.xml")

#simulacao.create_drone_angular((-73.983754,40.745802),40)
simulacao.create_drone_circular((-73.986478,40.744406),40)
#simulacao.create_drone_tractor((-73.983754,40.745802),70,100,6,orientation="vertical")
#simulacao.print_all_vehicle_info("drone1")

limits = ((-73.986912,40.745779),(-73.987874,40.744475),(-73.985928,40.743628),(-73.985150,40.744933))

#simulacao.export_to_video("circular",limits_map=limits,only_vants=1)
simulacao.export_to_video("circular2",only_vants=1)


#test trace exporter
#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattan.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattan.tcl

#Test Manhattan Scenario
#sumo -c C:\Users\Pichau\Desktop\manhattan_cenario_SBRC-master\medio\medio.sumocfg --fcd-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattan.xml --fcd-output.geo true
