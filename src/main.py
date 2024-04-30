from HTML import fileupload

'''if __name__ == '__main__':
    fileupload.app.run(debug=True)
'''

import src.functions as f

df = f.countemployees('/Users/marco/Developer/GitHub/Botteg52/xlsx files/InputData.xlsx')

f.file_sguccer(f.create_buyers('/Users/marco/Developer/GitHub/Botteg52/xlsx files/Categories.xlsx'), f.create_targets('/Users/marco/Developer/GitHub/Botteg52/xlsx files/Categories.xlsx'), f.create_influencers('/Users/marco/Developer/GitHub/Botteg52/xlsx files/Categories.xlsx'), df)


