import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 설정
st.set_page_config(page_title="이경원의 수학연구소", layout="wide")
SHEET_NAME = "이경원의 수학연구소 관리 데이터"

@st.cache_data(ttl=600)
def load_data(tab_name):
    try:
        # 1. Secrets에서 딕셔너리로 직접 가져오기 (가장 확실한 방법)
        s_info = st.secrets["gcp_service_account"]
        
        # 2. 딕셔너리 형태로 강제 변환
        info = {k: v for k, v in s_info.items()}
        
        # 3. 열쇠 줄바꿈 강제 수선
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        # 4. 최신 인증 방식
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        
        sh = client.open(SHEET_NAME)
        return pd.DataFrame(sh.worksheet(tab_name).get_all_records())
    except Exception as e:
        # 어디서 에러가 났는지 상세히 출력
        st.error(f"❌ 데이터 연결 실패: {str(e)}")
        if "PEM" in str(e):
            st.warning("⚠️ 원인: 열쇠(Private Key) 형식이 틀립니다. Secrets의 내용을 확인해주세요.")
        return pd.DataFrame()

# 관리자 페이지 및 리포트 로직
sid = st.query_params.get("id")
if sid:
    df_s = load_data("Student_Master")
    # ... (데이터 출력 로직)
else:
    st.title("🛡️ 관리자 페이지")
    st.info("주소창 끝에 /?id=학생코드 를 입력하면 리포트가 뜹니다.")
