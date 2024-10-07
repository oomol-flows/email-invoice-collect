from oocana import Context
import pandas as pd
import os

output_file_dir = "/app/workspace/output_file"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main(inputs: dict, context: Context):
  ensure_dir(output_file_dir)
  map1 = inputs.get("map1")
  
  # TODO 从多个源获取 map 然后合并
  df = pd.DataFrame(data=map1, index=[0])

  df = (df.T)

  print (df)

  df.to_excel(os.path.join(output_file_dir, 'output.xlsx'))