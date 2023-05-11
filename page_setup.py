import streamlit as st
from PIL import Image


def set_config():
    st.set_page_config(
    page_title="催老師審稿小工具",
    page_icon="📚",
    initial_sidebar_state="expanded"
)
    st.title('JCIE 催老師審稿小工具')
    st.info('只要把系統下載的CSV檔丟上來，就可以幫你擷取出「催老師審稿」的名單喔！')

def set_sidebar():
    with st.sidebar:
        st.header('SOP')
        st.write('1. 登入 ScholarOne Manuscripts')
        st.write('2. 點擊 Manage/Editorial Office Centre')
        st.write('3. 點擊你目前正在整理的 Section，例如"Assign AE"')
        st.write('4. 在頁面底部找到 Export to CSV 的按鈕（如下），點擊後會跳出下載小視窗，再點擊裡面的 "Click" 即可下載 CSV 檔')  
        st.image(Image.open('2.png'),width=150)
        st.write('5. 回到這裡，上傳剛剛下載的CSV檔')  
        st.write('6. 按下執行按鈕')  
        st.info('備註：建議使用 Google Sheet 開啟完成的檔案，這樣才不會有亂碼喔！(會儘快修復這個小bug 🥺)')  
        st.warning('注意：如果 note 欄位的尚需N位審查者出現<=0的數字，這代表 reviewes required to make decision 不為 2，要再自行查詢正確人數！', icon="⚠️")
        st.warning('詳細的教學，請參見：reurl.cc/2W2eov', icon="⚠️")