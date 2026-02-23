import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# 설정
st.set_page_config(page_title="이경원의 수학연구소", layout="wide")
SHEET_NAME = "이경원의 수학연구소 관리 데이터"

@st.cache_data(ttl=600)
def load_data(tab_name):
    try:
        # [핵심] Secrets에서 'json_key'라는 이름으로 통째로 가져옵니다
        json_key_str = st.secrets["gcp_service_account"]["json_key"]
        info = json.loads(json_key_str) # 문자열을 실제 열쇠로 변환
        
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        
        sh = client.open(SHEET_NAME)
        return pd.DataFrame(sh.worksheet(tab_name).get_all_records())
    except Exception as e:
        st.error(f"❌ 데이터 연결 실패: {e}")
        return pd.DataFrame()

# 관리자 및 리포트 로직은 기존과 동일...
sid = st.query_params.get("id")
if sid:
    df_s = load_data("Student_Master")
    # (이후 출력 로직)
else:
    st.title("🛡️ 관리자 페이지")
    st.info("주소창 끝에 /?id=학생코드를 입력하세요.")
