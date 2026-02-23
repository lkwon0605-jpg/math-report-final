import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
import datetime
import math

# [기본 설정]
st.set_page_config(page_title="이경원의 수학연구소", layout="wide")
SHEET_NAME = "이경원의 수학연구소 관리 데이터"

# [데이터 로드 함수 - 무적 버전]
@st.cache_data(ttl=600)
def load_data(tab_name):
    try:
        # Secrets에서 정보 가져오기
        info = st.secrets["gcp_service_account"]
        if hasattr(info, "to_dict"):
            info = info.to_dict()
        
        # 65자/PEM 에러 강제 치료
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        # 최신 gspread 방식 (훨씬 에러가 적습니다)
        client = gspread.service_account_from_dict(info)
        sh = client.open(SHEET_NAME)
        return pd.DataFrame(sh.worksheet(tab_name).get_all_records())
    except Exception as e:
        st.error(f"⚠️ 연결 오류: {e}")
        return pd.DataFrame()

# (이하 원장님의 시각화 로직은 그대로 유지됩니다...)
sid = st.query_params.get("id")
if sid:
    df_s = load_data("Student_Master")
    if not df_s.empty:
        df_s.columns = df_s.columns.str.replace(' ', '')
        user = df_s[df_s['고유코드'].astype(str) == str(sid)]
        if not user.empty:
            name, cls = user.iloc[0]['이름'], user.iloc[0]['클래스']
            st.markdown(f"<h2>{name} 학생 리포트</h2>", unsafe_allow_html=True)
            # ... 나머지 디자인 생략 (기존 코드 유지)
else:
    st.title("🛡️ 관리자 페이지 (/?id=코드 를 입력하세요)")
