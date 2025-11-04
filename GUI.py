#Import needed for GUI:
import PySimpleGUI as sg
import math
import pandas as pd


class GUI:
  #Constructor
  def __init__(self):
    self.theme=sg.theme('DefaultNoMoreNagging') #GUI theme name

    #Window components
    self.layout = [
    #Labels & inputs:
    [sg.Text('Enter demand table, newsday type table, cost, price, scrap price, bundle size, and number of days:', size =(100, 2))],
    [sg.Text('Demand table:', size =(26, 2)), sg.FileBrowse(key="demand")],
    [sg.Text('Newsday type table:', size =(26, 2)), sg.FileBrowse(key="newsdays")],
    [sg.Text('Cost of buying (1) newspaper:', size =(26, 2)),sg.InputText(key="cost")],
    [sg.Text('Price of selling (1) newspaper:', size =(26, 2)),sg.InputText(key="price")],
    [sg.Text('Scrap price of selling (1) newspaper:', size =(26, 2)),sg.InputText(key="scrap_price")],
    [sg.Text('Bundle size:', size =(26, 2)),sg.InputText(key="bundle_size")],
    [sg.Text('Number of days:', size =(26, 2)),sg.InputText(key="days")],
    #Buttons:
    [sg.Submit(), sg.Cancel()]]
    
    self.window = sg.Window('Input window', self.layout, size=(650,400))
    

  def readInput(self):
    while True:
        event, values = self.window.read() #Returns list of inputs
        if event == sg.WIN_CLOSED:
          break
        elif event == "Submit":
          demand = values["demand"] #CSV or xlsx file
          newsdays = values["newsdays"] #CSV or xlsx file
          cost = values["cost"] #Cost of newspaper
          price = values["price"] #Price of selling one newspaper
          scrap_price = values["scrap_price"] #Price of selling one newspaper as scrap
          bundle_size = values["bundle_size"]
          days = values["days"]
          print(values) #Checking 
          self.window.close() #Closing window after getting all inputs
    return demand, newsdays,cost,price,scrap_price,bundle_size,days #Returning input values

  #Output window for the results of the simulation
  def output(self,currentBundleSize,recommendedQ,profit_of_recommendedQ,simulationRuns,AverageDemand,profit_of_AverageDemand,decisionQ,decisionB):
      label1='Current bundle size :'+ str(currentBundleSize)
      label2='Recommended newspaper quantity for current bundel size (simulation result) : '+str(recommendedQ)
      label3='Total profit from selling '+str(recommendedQ)+ ' newspapers :'+str(profit_of_recommendedQ)+'$'
      label4='Average demand from '+str(simulationRuns)+' Simulation runs :'+str(AverageDemand)
      label5='Total profit from selling '+str(math.ceil(AverageDemand))+ ' newspapers :'+str(profit_of_AverageDemand)+'$'
      label6='Decision is to sell '+str(decisionQ)+' newspapers with bundel sizes of : '+str(decisionB)
      layout = [
      [sg.Text(label1, size =(100, 2))],
      [sg.Text(label2, size =(100, 2))],
      [sg.Text(label3, size =(100, 2))],
      [sg.Text(label4, size =(100, 2))],  
      [sg.Text(label5, size =(100, 2))],  
      [sg.Text(label6, size =(100, 2))],  
      [sg.Ok()]]
      window = sg.Window('Results',layout, size=(600,340))
      while True:
        event, values = window.read()
        if event is None or event =='Ok':
          break
      window.close()






