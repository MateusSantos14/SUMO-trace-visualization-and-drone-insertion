from Simulation import Simulation
from Tools import FilterTimesteps
'''

simulacao = Simulation("Traces/osmWithStop.xml")

simulacao.create_drone_following("f_0.0",4)
simulacao.create_drone_circular((-38.576, -3.74204395),10,6)

simulacao.print_all_vehicle_info("drone1")

simulacao.export_timesteps_to_xml("teste.xml")

simulacao.export_to_video("simulation_video")

'''

#test trace exporter
#py 'C:\Program Files (x86)\Eclipse\Sumo\tools\traceExporter.py' --fcd-input C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\teste.xml --ns2mobility-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\mobility.tcl
#traceExporter --fcd-input myFCDOutput.xml --ns2mobility-output myMobilityTrace.tcl --proj.utm <UTM_zone>

#Test Luxemburgo Scenario
#sumo -c C:\Users\Pichau\Desktop\LuSTScenario-master\scenario\dua.static.sumocfg --fcd-output C:\Users\Pichau\Desktop\Faculdade\UFC\BOLSA\2024Project\main.py --fcd-output.geo true

'''
simulacao = Simulation("Traces/outputwithlimits.xml")
simulacao.export_to_video("VideoGenerated/simulation_video")
'''