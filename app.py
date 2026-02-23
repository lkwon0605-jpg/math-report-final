import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="이경원의 수학연구소", layout="wide")
SHEET_NAME = "이경원의 수학연구소 관리 데이터"

@st.cache_data(ttl=600)
def load_data(tab_name):
    try:
        # Secrets에서 모든 정보를 딕셔너리로 읽어옴
        info = dict(st.secrets["gcp_service_account"])
        # 줄바꿈 수선
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(info, scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        client = gspread.authorize(creds)
        sh = client.open(SHEET_NAME)
        return pd.DataFrame(sh.worksheet(tab_name).get_all_records())
    except Exception as e:
        st.error(f"❌ 데이터 연결 실패: {e}")
        return pd.DataFrame()

sid = st.query_params.get("id")
if sid:
    df_s = load_data("Student_Master")
    if not df_s.empty:
        df_s.columns = df_s.columns.str.replace(' ', '')
        user = df_s[df_s['고유코드'].astype(str) == str(sid)]
        if not user.empty:
            st.title(f"📊 {user.iloc[0]['이름']} 학생 리포트")
            st.success("데이터 로드 완료!")
        else:
            st.warning(f"ID {sid}번 학생을 찾을 수 없습니다.")
else:
    st.title("🛡️ 관리자 페이지 (/?id=코드 를 입력하세요)")
