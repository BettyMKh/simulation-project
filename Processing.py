import pandas as pd

class Processing:
  #Constructor
  def __init__(self) -> None:
        pass

  def process(self,CSV):
    processed_dataframe = pd.read_csv(CSV)
    processed_dataframe=(processed_dataframe).dropna() #Dropping null values
    processed_dataframe=(processed_dataframe).drop_duplicates() #Dropping duplicates
    processed_dataframe.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True) #Replacing characters that might resut from conversion
    return processed_dataframe #Returnning the processed dataframe
 
  def saveDataframe(self,dataframe,file_dir):
    writer = pd.ExcelWriter(file_dir) 
    dataframe.to_excel(writer) #Writes given dataframe into a given excel file directory
    writer.save() #Saves the excel file
  
  #Destructor
  def __del__(self):
        print('')
