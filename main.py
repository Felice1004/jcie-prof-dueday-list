import pandas as pd
import streamlit as st
import re
from datetime import datetime
import csv
import io

def dict_to_csv(data):
    csv_string = io.StringIO()
    csv_writer = csv.writer(csv_string)
    csv_writer.writerow(['ID','COEIC', 'AE' ,'OVERDUE', 'STATUS','NOTE'])
    for key, value in data.items():
        content = [key]
        for info in value:
          content.append(info)
        csv_writer.writerow(content)
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

      #尋找出現「#EIC:」的座標
      index = cooking_txt.strip().find("#EIC:")


      #審查狀態
      for status in paper_status:
        if status in original_txt:
          rows[id] = [cooking_txt[:index]+'#',overdue_days,'#'+status] # 輸出CEIC+AE、逾期天數、審查狀態，並以#隔開
          break
  return rows, status

def csv_pretty(data):
    result = {}
    for key in data:
      result[key]=[]
      for content in data[key]:
        if 'CEIC' not in content:
          content = content.split('#')
          content = list(filter(None, content))
          result[key].append(content)
        else:
          content = content.replace('CEIC: ','')
          content = content.replace('#','')
          content = content.strip()
          content = content.split('AE:')
          for prof in content:
            result[key].append(prof)

        
    st.write(result)
    return result
   


st.set_page_config(
   page_title="JCIE 資料清洗小工具",
   page_icon="🧽",
   layout="wide",
   initial_sidebar_state="expanded",
)

paper_status = ['Assign Reviewer', 'Select Reviewer', 'Invite Reviewer', 'Awaiting Reviewer Scores', 'AE Makes Recommendation', 'CO-EIC Makes Recommendation', 'Awaiting AE Assignment', 'Make Decision']
output_data = {}
status = ""


st.title('JCIE 催老師審稿小工具')
st.info('只要把系統下載的CSV檔丟上來，就可以幫你擷取出「催老師審稿」的名單喔！')

uploaded_file = st.file_uploader("Choose a csv file")
columns=['Manuscript ID','Manuscript Title','Manuscript Type','Data Submitted', 'Submitting Author','Country of Submitting Author', 'Editor In Chief', 'Editor','Status','Manuscript Flag', 'Unnamed']
data = pd.DataFrame(columns=columns)
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data.rename(columns={'ï»¿"Manuscript ID"': 'ID'}, inplace=True)
    data.rename(columns={'Manuscript ID': 'ID'}, inplace=True)
    st.write('Preview data')
    st.write(data)

task_finished = False

if st.button('Execute'):
  with st.spinner('Wait...'):
    output_data, status = process_raw_csv(output_data, data)
    output_data = csv_pretty(output_data)
    st.success('Done')
    task_finished = True


now = datetime.now()
timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")

csv_data = dict_to_csv(output_data)

if task_finished:
  st.download_button(
  label="Download Result",
  data=csv_data,
  file_name=f'{status}-jcie-{timestamp}.csv',
  mime='text/csv')