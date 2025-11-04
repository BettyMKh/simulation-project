#Imports needed:
import numpy as np 
import pandas as pd 
import random
import Processing
from pandasgui import show
#show()
    
#This class is concerned with filling the tables required to begin the process of simulation
class Tables:
    def __init__(self,demand, newsdays,cost,price,scrap_price,supply_quantity,days):

        pd.set_option('display.float_format', lambda x: '%.3f' % x) #Formatting output and removes scientific notation
        #User inputs
        self.demand=demand
        self.newsdays=newsdays
        self.cost=cost
        self.price=price
        self.scrap_price=scrap_price
        self.supply_quantity=supply_quantity
        self.days=days
        self.pro=Processing.Processing()

        #Tables that will be filled 
        self.demandProbability = self.demand.drop(self.demand.columns[0], axis=1)#Dropping column indices
        self.demandCummProbability = pd.DataFrame(columns=self.demandProbability.columns,index=range(0, self.demandProbability.shape[0]))
        self.demandRDA = pd.DataFrame(columns=self.demandProbability.columns+[' RDA'],index=range(0, self.demandProbability.shape[0]))
        self.newsDaysProbability=pd.array(self.newsdays.iloc[:,1])
        self.newsDaysCummProbability=[]
        self.newsDaysRDA=[]
        self.simulationTable=pd.DataFrame(columns=['Newsday RDA','Newsday Type','Demand RDA','Supply','Demand','Sales Revenue','Lost Profit From Excess Demand','Salvage','Daily Profit'])
    
    #Will explain in discussion
    def getDigits(self,n):
        if(n>=0.1 and n <0.11):
            return min((n*10)+1,100)
        else:
            return min((n*100)+1,100)         
    
    #Calculates cummulative probability for the newsdays probability distribution table
    def calcNewsDaysCummProbability(self):
        for i in range(0,len(self.newsDaysProbability)):
            if (i==0):
                self.newsDaysCummProbability.append(self.newsDaysProbability[i])
            else:
                self.newsDaysCummProbability.append(self.newsDaysCummProbability[i-1]+self.newsDaysProbability[i])
    
    #Calculates RDA for the newsdays probability distribution table given cummulative probability 
    def calcNewsDaysRDA(self):
        for i in range(0,len(self.newsDaysProbability)):
            if (i==0):
                self.newsDaysRDA.append(0) #Starting interval is from zero, also will explain in discussion
            else:
                self.newsDaysRDA.append(self.getDigits(self.newsDaysCummProbability[i-1]))
        
        #Appending in newsdays table
        self.newsdays['Cummulative Probability']=self.newsDaysCummProbability
        self.newsdays['RDA']=self.newsDaysRDA

    #Calculates cummulative probability for the demand probability distribution table
    def calcDemandCummProbability(self):
        for i in range(0,self.demandCummProbability.shape[0]):
            if (i==0):
                self.demandCummProbability.iloc[0,:]=self.demandProbability.iloc[0,:]
            else:
                self.demandCummProbability.iloc[i,:]=self.demandProbability.iloc[i,:]+self.demandCummProbability.iloc[i-1,:]
        #Adding "_cumm" to distinguish calculations
        self.demandCummProbability=self.demandCummProbability.add_suffix(' _cumm')

    #Calculates RDA for the demand probability distribution table given cummulative probability 
    def calcDemandRDA(self):
        for i in range(0,self.demandRDA.shape[0]): 
            if (i==0):
                self.demandRDA.iloc[0,:]=0
            else:
                self.demandRDA.iloc[i,:]=(self.demandCummProbability.iloc[i-1,:]).apply(self.getDigits)

        #Concatinates calculated demand cummulative probability and demand RDA
        self.demand = pd.concat([self.demand, self.demandCummProbability, self.demandRDA], axis=1, join='inner')
      
    #Generates random numbers for newsdays and demand RDAs
    def RDA(self):
        #Generates a list of random numbers in range [0:100] and length of [days] 
        nRDA = random.sample(range(0, 100), self.days) 
        dRDA = random.sample(range(0, 100), self.days)

        #Fills the given columns in simulation table 
        self.simulationTable['Newsday RDA'] = nRDA 
        self.simulationTable['Demand RDA'] = dRDA
    
    #Assigns the type of newsday according to [Newsday RDA]
    def newsdayType(self):
        t_copy= self.newsdays['Type']
        t=pd.array(t_copy)
    
        nRDA_copy=self.newsdays['RDA'] #RDA in newsdays type table
        nRDA=pd.array(nRDA_copy)
    
        sRDA_copy=self.simulationTable['Newsday RDA'] #RDA in simulation table
        sRDA=pd.array(sRDA_copy)

        val=[] #Will be appending 
        for i in range (0,len(sRDA)):
            for j in range (0,len(nRDA)):
                if(sRDA[i]>= nRDA[j]):
                    if(j!= len(nRDA)-1):
                        if(sRDA[i]<nRDA[j+1]):
                            val.append(t[j])
                    else:
                        val.append(t[j])
        #print(val) << Checking
        val=pd.DataFrame(val) #Converting the list of results into a pandas dataframe
        self.simulationTable['Newsday Type']=val #Appending the resulting dataframe into this column
    
    #Getting the value of demand according to the type of newsday
    def demandValue(self):
        nType_copy=self.simulationTable['Newsday Type']
        nType=pd.array(nType_copy)
    
        dRDA_copy=self.simulationTable['Demand RDA']
        dRDA=pd.array(dRDA_copy)
    
        dValue_copy=self.demand['demand']
        dValue=pd.array(dValue_copy)
    
        val=[]
        for i in range (0,len(dRDA)):
            key= nType[i]+' RDA'
            Vcopy=self.demand[key]
            Values=pd.array(Vcopy)
            #print(Values)
            for j in range (0,len(Values)):
                if(dRDA[i]>= Values[j]):
                    if(j!= len(Values)-1):
                        if(dRDA[i]<Values[j+1]):
                            #print(dValue[j]) <<checking
                            val.append(dValue[j])
                    else:
                        val.append(dValue[j])
        val=pd.DataFrame(val)
        #print(val) <<checking
        self.simulationTable['Demand']=val
    
    #Calculates the revenue of each day
    def salesRevenue(self):
        copy=self.simulationTable['Demand']
        dValue=pd.array(copy)

        revenueList=[]
        lostProfitList=[]
        salvageList=[]
        costList=[]

        self.simulationTable.loc[:, 'Supply'] = self.supply_quantity

        for i in range (0,len(dValue)):
            costList.append(self.supply_quantity*self.cost)
            #If the value of demand is less than supply, then:
            if(dValue[i]<=self.supply_quantity):
               #The revenue is the demand multiplied by selling price
               revenue=dValue[i]*self.price
               revenueList.append(revenue)
            
               #No lost profit due to excess demand, append zero
               lostProfitList.append(0) 
               
               #Salvage is the difference between supply and demand multiplied by salvage price
               salvage=(self.supply_quantity-dValue[i])*self.scrap_price 
               salvageList.append(salvage)
            
            else:
               #The revenue is the supply quantity multiplied by selling price
               revenue=self.supply_quantity*self.price
               revenueList.append(revenue)
               
               """
               Lost profit due to excess demand is the difference between demand and supply 
               multiplied by the difference between selling price and cost of newspaper
               """
               lostProfit=(dValue[i]-self.supply_quantity)*(self.price-self.cost)
               lostProfitList.append(lostProfit)
               
               #No excess newspapers sold as scrap, append zero
               salvageList.append(0)

        self.simulationTable['Cost']=pd.DataFrame(costList)
        self.simulationTable['Sales Revenue']=pd.DataFrame(revenueList)
        self.simulationTable['Lost Profit From Excess Demand']=pd.DataFrame(lostProfitList)
        self.simulationTable['Salvage']=pd.DataFrame(salvageList)
    

    def dailyProfit(self):
    #Profit = revenue from sales − cost of newspapers − lost profit from excess demand + salvage from sale of scrap papers
        revenue_copy=self.simulationTable['Sales Revenue']
        revenue=pd.array(revenue_copy)
    
        lostProfit_copy=self.simulationTable['Lost Profit From Excess Demand']
        lostProfit=pd.array(lostProfit_copy)
                          
        salvage_copy=self.simulationTable['Salvage']
        salvage=pd.array(salvage_copy)
    
        cost_copy=self.simulationTable['Cost']
        cost=pd.array(cost_copy)

        dcopy=self.simulationTable['Demand']
        demand_value=pd.array(dcopy)

    
        profitList=[] 
        
        """
        Profit = [(revenue from sales) – (cost of newspapers) – 
        (lost profit from excess demand) + (salvage from sale of scrap papers)]
        """
        for i in range (0,len(revenue)):
            """
            Profit could be calculated this way, which answers the question:
                Q(2) How does the price of selling the newspaper and of selling the unsold newspapers as
                    a scrap affect your answer (the optimal number to purchase)?
                >> Because selling news paper as scrap is less than the cost of news paper, so it's considered a loss
                  that affects the total profit i.e. it's subtracted from the revenue.
            """
            if(self.supply_quantity>demand_value[i]):
                profit=revenue[i]-(self.cost*demand_value[i])-((self.cost-self.scrap_price)*(self.supply_quantity-demand_value[i]))
            else:
                profit=revenue[i]-cost[i]-lostProfit[i]
            
            
            """

            Profit could also be calculated this way from lecture slides, but it does not show the relationship 
            between the scrap price and how it affects the value of total profit:

            profit=revenue[i]-cost[i]-lostProfit[i]+salvage[i]

            """
            profitList.append(profit)
        
        self.simulationTable['Daily Profit']=pd.DataFrame(profitList)
    
    #Calls all functions and fills the columns of simulation table
    #Newsday RDA,Newsday Type,Demand RDA,Supply,Demand,Sales Revenue,Lost Profit From Excess Demand,Salvage,Daily Profit
    def fillSimulationTable(self):
        self.calcNewsDaysCummProbability()
        self.calcNewsDaysRDA()
        self.calcDemandCummProbability()
        self.calcDemandRDA()
        self.RDA()
        self.newsdayType()
        self.demandValue()
        self.salesRevenue()
        self.dailyProfit()

        #Returns the calulated simulation table
        return(self.simulationTable)
    
    #Verifying mathematically
    """
    def criticalRatio(self):
       shortage= self.price - self.cost
       excess_cost= self.cost - self.scrap_price
       critical_ratio = shortage/ (excess_cost + shortage)
       return critical_ratio
    """
    
    #Returns demand table
    def getDemandTable(self):
        return(self.demand)

    #Returns newsdays table
    def getNewsDaysTable(self):
        return(self.newsdays)
        
    #Returns the sum of [Lost Profit From Excess Demand] column from simulation table
    def getTotalLostProfit(self):
        self.simulationTable=self.simulationTable.reset_index(drop=True)
        return(self.simulationTable['Lost Profit From Excess Demand'].sum())
    
    #Returns the sum of [Daily Profit] column from simulation table
    def getTotalProfit(self):
        return(self.simulationTable['Daily Profit'].sum())


    #Destructor
    def __del__(self):
        print('')



        
