import GUI
import Simulator

             
input = GUI.GUI()
demand,newsdays,cost,price,scrap_price,bundle_size,days=input.readInput()

simulator= Simulator.Simulator(demand, newsdays,cost,price,scrap_price,bundle_size,days,10) #10 simulation runs
simulator.simulate()
simulator.simulateAvgDemand()
simulator.decide()
simulator.extraStatistics()
simulator.print()

