from Simulation import Simulation
from Tools import FilterTimesteps


simulacao = Simulation("manhattan.xml")

simulacao.create_drone_angular((-73.983754,40.745802),40)

simulacao.print_all_vehicle_info("drone1")

simulacao.export_to_video("simulation_video2")


#test trace exporter
#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattan.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattan.tcl

#Test Manhattan Scenario
#sumo -c C:\Users\Pichau\Desktop\manhattan_cenario_SBRC-master\denso\denso.sumocfg --fcd-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\manhattandenso.xml --fcd-output.geo true
