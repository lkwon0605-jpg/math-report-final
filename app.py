import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# 기본 설정
st.set_page_config(page_title="이경원의 수학연구소", layout="wide")
SHEET_NAME = "이경원의 수학연구소 관리 데이터"

@st.cache_data(ttl=600)
def load_data(tab_name):
    try:
        # Secrets에서 열쇠 가져오기
        s_info = st.secrets["gcp_service_account"]
        info = {k: v for k, v in s_info.items()}
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        
        sh = client.open(SHEET_NAME)
        return pd.DataFrame(sh.worksheet(tab_name).get_all_records())
    except Exception as e:
        st.error(f"❌ 연결 오류: {e}")
        return pd.DataFrame()

# 실행 로직
sid = st.query_params.get("id")

if sid:
    st.info(f"입력된 ID: {sid} - 데이터를 조회 중입니다...")
    df_s = load_data("Student_Master")
    
    if not df_s.empty:
        # 제목의 공백 제거
        df_s.columns = df_s.columns.str.replace(' ', '')
        
        # [진단용] 데이터가 잘 왔는지 확인하기 위해 상위 3줄만 보여줍니다
        # st.write("데이터 연결 성공! 시트 내용 일부:", df_s.head(3)) 
        
        user = df_s[df_s['고유코드'].astype(str) == str(sid)]
        
        if not user.empty:
            name = user.iloc[0]['이름']
            st.success(f"✅ {name} 학생의 데이터를 찾았습니다!")
            st.title(f"📊 {name} 학생 주간 리포트")
            # 여기에 그래프 코드가 이어집니다...
        else:
            st.warning(f"⚠️ '{sid}'와 일치하는 학생 정보를 시트에서 찾을 수 없습니다.")
            st.write("시트에 등록된 고유코드 예시:", df_s['고유코드'].unique()[:5])
    else:
        st.error("시트에서 데이터를 가져오지 못했습니다. 탭 이름을 확인하세요.")
else:
    st.title("🛡️ 관리자 페이지")
    st.write("주소창 끝에 **?id=코드**를 붙여주세요. (예: ...streamlit.app/?id=1111)")
