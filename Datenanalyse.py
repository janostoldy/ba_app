from galvani import BioLogic
import pandas as pd

def analyze_data(file_path, cycle):


    for data_name in file_path:
        #print('Processing: ' + os.path.basename(data_name))
        mpr_file = BioLogic.MPRfile('00_Test_Data/test.mpr')
        df = pd.DataFrame(mpr_file.data)
