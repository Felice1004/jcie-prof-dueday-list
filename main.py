import pandas as pd
import streamlit as st
import re
from datetime import datetime
import csv
import io
from PIL import Image

import data_retriever as dr
import page_setup as ps

def dict_to_csv(data):
    csv_string = io.StringIO()
    csv_writer = csv.writer(csv_string)
    csv_writer.writerow(['ID','COEIC', 'AE' ,'OVERDUE', 'STATUS','NOTE'])
    for id, cols_dump in data.items():
        cols = [id]
        for col in cols_dump:
          cols.append(col)
        csv_writer.writerow(cols)
    return csv_string.getvalue()

def process_raw_csv(rows, data):
  status = ""
  for id in data['ID']:
    for cooking_txt in data.Status[data['ID']==id]:
      original_txt = cooking_txt
      # 從「Status」欄位中尋找過期天數
      match = re.search(r'\d+ days overdue', cooking_txt)
      overdue_days = 0
      if match:
        overdue_days = match.group(0)
        match = re.search(r'\d+', overdue_days) #只取逾期的天數。例如 5 days overdue，就只取 5
        overdue_days = match.group(0)
        print("Found match:", match.group(0))
      else:
          #代表這筆論文的處理並沒有逾期，直接省略
        continue
      cooking_txt = cooking_txt.strip().replace('\r\n','#')

      #審查狀態
      for status in paper_status:
        if status in original_txt:
          note=''
          if status == 'Assign Reviewer':
            match = re.search(r'\d+ agreed', cooking_txt)
            note = match.group(0)
            match = re.search(r'\d+', note)
            note = 2 - int(match.group(0)) #尚需n位審查者
            if note != 0:
              note = str(note)
              note = f'尚需邀請到{note}位審查者'
          elif status == 'Awaiting AE Assignment' or status == 'AE Makes Recommendation' or status == 'CO-EIC Makes Recommendation':
            note ='-'
          elif (status !='Assign AE') & (status !='Select Reviewer') & (status!='Invite Reviewer'):
            match = re.search(r'\d+ returned', cooking_txt)
            note = match.group(0)
            match = re.search(r'\d+', note)
            note = 2 - int(match.group(0)) #尚需n位審查者
            if note != 0:
              note = str(note)
              note = f'尚需{note}位審查者回覆'

          index = cooking_txt.strip().find("#EIC:")
          rows[id] = [cooking_txt[:index]+'#',overdue_days,'#'+status,'#'+str(note)] # 輸出CEIC+AE、逾期天數、審查狀態、尚需n位審查者，並以#隔開
          break
  return rows

def csv_pretty(data):
    result = {}
    for key in data:
      result[key]=[]
      for content in data[key]:
        if 'CEIC' not in content:
          content = content.split('#')
          content = list(filter(None, content))
          for info in content:
            result[key].append(info)
        else:
          content = content.replace('CEIC: ','')
          content = content.replace('#','')
          content = content.strip()
          content = content.split('AE: ')
          for prof in content:
            result[key].append(prof)

    return result


if __name__ == "__main__":

  columns= dr.txt2list('config/exported_col_names.txt')
  paper_status = dr.txt2list('config/paper_status_list.txt')
  output_data = {}

  ps.set_config()
  ps.set_sidebar()

  st.header('上傳檔案')
  uploaded_file = st.file_uploader("Choose a csv file")
  data = pd.DataFrame(columns=columns)

  task_finished = False

  if uploaded_file is not None:
      data = pd.read_csv(uploaded_file)
      data.rename(columns={'ï»¿"Manuscript ID"': 'ID'}, inplace=True)
      data.rename(columns={'Manuscript ID': 'ID'}, inplace=True)
      st.write('Preview data')
      st.write(data)
      if st.button('執行'):
        with st.spinner('Wait...'):
          output_data = process_raw_csv(output_data, data)
          output_data = csv_pretty(output_data)
          st.success('Done')
          task_finished = True

  if task_finished:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
    csv_data = dict_to_csv(output_data)

    st.download_button(
    label="Download Result",
    data=csv_data,
    file_name=f'jcie-{timestamp}.csv')

    
    

