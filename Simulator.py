import numpy as np 
import pandas as pd 
import Tables
import Processing
import GUI
import math
import matplotlib.pyplot as plt

#Returns all possible bundle sizes for a recommended quantity 
def bundleSize(recommended_quantity):
    count = 1
    bundle_list=[]
    while count <= recommended_quantity :
        if (recommended_quantity % count==0) :
            bundle_list.append(count) #Checks all numbers that are divisible by the recommended quantity
        count = count + 1

    if len(bundle_list)<=4: #To ensures there are plenty of options regarding the bundle size    
        return bundleSize(round(recommended_quantity / 2)* 2) #Returns the nearist even number
    else:
        return bundle_list
          

class Simulator:
    def __init__(self,demand,newsdays,cost,price,scrap_price,bundle_size,days,simulation_runs):
        self.pro=Processing.Processing()
        self.demand=self.pro.process(demand)
        self.newsdays=self.pro.process(newsdays)
        self.cost=float(cost)
        self.price=float(price)
        self.scrap_price=float(scrap_price)
        self.bundle_size=int(bundle_size)
        self.days=int(days)
        self.simulation_runs=int(simulation_runs)

        self.demand_mean=0 #Demand average
        self.recommendedQ=0 #Recommended quantity resulting from simulating different supply values
        self.profit_of_recommendedQ=0 #Total profit of recommended quantity
        self.profit_of_average_demand=0 #Total profit of average demand quantity
        self.decisionQ=0 #Final dicision quantity
        self.decisionB=0 #Final decision bundle sizes
        
        #Stores calculated values resulting from simulating different supply values
        self.conclusionTable=pd.DataFrame(columns=['Supply','Total Lost Profit','Total Daily Profit'])

        #Stores calculated values resulting from simulating the demand mean as supply quantity
        self.avgDemandTable=pd.DataFrame(columns=['Supply','Total Lost Profit','Total Daily Profit'])

        #Stores all simulation results
        self.simulationTable=pd.DataFrame(columns=['Newsday RDA','Newsday Type','Demand RDA','Supply','Demand','Sales Revenue','Lost Profit From Excess Demand','Salvage','Daily Profit'])
    
    #Gets the demand range in demand distribution table to simulate supply values accordingly
    def getDemandRange(self):
        demandList=self.demand['demand']
        demandList=np.array(demandList)
        self.minRange=demandList.min()
        self.maxRange=demandList.max()
    
    #Simulating different supply values
    def simulate(self):

        #Storing
        supplyList=[]
        Lost_Profit=[]
        Daily_Profit=[]

        self.getDemandRange()
        for supply in range(self.minRange, self.maxRange+1, self.bundle_size): #bundle_size as step size
            for counter in range (0,self.simulation_runs+1):
                table=Tables.Tables(self.demand, self.newsdays,self.cost,self.price,self.scrap_price,supply,self.days)
                self.simulationTable =self.simulationTable.append(table.fillSimulationTable(), ignore_index = True)
            supplyList.append(supply)
            Lost_Profit.append(table.getTotalLostProfit())
            Daily_Profit.append(table.getTotalProfit())
        
        self.demandMean=self.simulationTable['Demand'].mean() #Calulating demand mean
        self.conclusionTable['Supply']=pd.DataFrame(supplyList)
        self.conclusionTable['Total Lost Profit']=pd.DataFrame(Lost_Profit)
        self.conclusionTable['Total Daily Profit']=pd.DataFrame(Daily_Profit)
        
        self.profit_of_recommendedQ=self.conclusionTable['Total Daily Profit'].max() #Getting maximum profit

        #Getting row index where [Total Daily Profit] is max then reflecting it on supply value
        self.recommendedQ= self.conclusionTable.loc[self.conclusionTable['Total Daily Profit'].idxmax(), 'Supply']
        
        #Sorrting the table according to supply values
        self.simulationTable=self.simulationTable.sort_values(by=['Supply'])

        #Copying data into excel files
        """

        self.pro.saveDataframe(self.simulationTable,'simulationTable.xlsx')
        self.pro.saveDataframe(table.getNewsDaysTable(),'newsdaysDistribution.xlsx')
        self.pro.saveDataframe(table.getDemandTable(),'demandDistribution.xlsx')

        """
        del table


    #Simulating demand mean as supply quantity
    def simulateAvgDemand(self):

        #Storing
        supplyList=[]
        Lost_Profit=[]
        Daily_Profit=[]
        for counter in range (0,self.simulation_runs+1):
            table=Tables.Tables(self.demand, self.newsdays,self.cost,self.price,self.scrap_price,int(math.floor(self.demandMean)),self.days)
            table.fillSimulationTable()

        supplyList.append(int(math.floor(self.demandMean)))
        Lost_Profit.append(table.getTotalLostProfit())
        Daily_Profit.append(table.getTotalProfit())

        self.avgDemandTable['Supply']=pd.DataFrame(supplyList)
        self.avgDemandTable['Total Lost Profit']=pd.DataFrame(Lost_Profit)
        self.avgDemandTable['Total Daily Profit']=pd.DataFrame(Daily_Profit)
        
        #Getting the sum of daily profit
        self.profit_of_average_demand=table.getTotalProfit()
        
        #Appending to conclusion table
        self.conclusionTable=pd.concat([self.conclusionTable, self.avgDemandTable], ignore_index=True)
        
        #Copying data into excel files
        """

        self.pro.saveDataframe(self.conclusionTable,'conclusionTable.xlsx')

        """
          
    """

    Decides which newspaper quantity results in maximum total profit:
    Profit resulting from simulating different supply values or Profit resulting from simulating the demand mean 
    as supply quantity

    """
    def decide(self):
        if(self.profit_of_recommendedQ>self.profit_of_average_demand):
            self.decisionQ=self.recommendedQ
            self.decisionB=bundleSize(self.recommendedQ)
        #If total profit is equal in both, then select the option with least ['Total Lost Profit'] value
        elif(self.profit_of_recommendedQ==self.profit_of_average_demand):
            if(self.conclusionTable['Total Lost Profit'].sum()>self.avgDemandTable['Total Lost Profit'].sum()):
                self.decisionQ=int(math.ceil(self.demandMean))
                self.decisionB=bundleSize(int(math.ceil(self.demandMean)))
            else:
                self.decisionQ=self.recommendedQ
                self.decisionB=bundleSize(self.recommendedQ)
        else:
            self.decisionQ=int(math.ceil(self.demandMean))
            self.decisionB=bundleSize(math.ceil(self.demandMean))

        #Output window
        gui=GUI.GUI()
        gui.output(self.bundle_size,self.recommendedQ,self.profit_of_recommendedQ,self.simulation_runs,
        self.demandMean,self.profit_of_average_demand,self.decisionQ,self.decisionB)
    
    #Calculates extra statistics for each newspaper quantity (min,max,mean)
    def extraStatistics(self):
        extraStat=self.simulationTable.groupby(['Supply']).agg({'Demand':['min','max','mean'],'Sales Revenue':['min','max','mean'],'Lost Profit From Excess Demand':['min','max','mean'],
        'Salvage':['min','max','mean'],'Daily Profit':['min','max','mean']})
        """
        self.pro.saveDataframe(extraStat,'extraStatistics.xlsx')
        
        """
        extraStat.plot(kind='bar')
        plt.legend()
        plt.show()

    
    def print(self):
        #Plotting the relationship between supply and total profit
        self.conclusionTable.plot(x='Supply', y='Total Daily Profit', kind='bar', label='Supply and Total Daily Profit', alpha=.6, edgecolor='white', color='red')
        
        #Plotting the relationship between supply and total lost profit
        self.conclusionTable.plot(x='Supply', y='Total Lost Profit', kind='bar',label='Supply and Total Lost Profit From Excess Demand', alpha=.6, edgecolor='white', color='red')
        plt.legend()
        plt.show()


    #Destructor
    def __del__(self):
        print('')
            

  


