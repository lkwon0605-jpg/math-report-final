import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
import datetime
import math

# [설정] 구글 시트 이름
SHEET_NAME = "이경원의 수학연구소 관리 데이터"

# 1. 데이터 로드 함수 (Secrets 금고에서 키를 꺼내옴)
@st.cache_data(ttl=600)
def load_data(tab_name):
    # 스트림릿 Secrets에 저장된 키 정보를 가져옵니다.
    creds_dict = dict(st.secrets["gcp_service_account"])
    # PEM 에러 방지: 줄바꿈 문자를 실제 엔터로 변환합니다.
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open(SHEET_NAME).worksheet(tab_name)
    return pd.DataFrame(sh.get_all_records())

# --- 선생님의 로컬 리포트 디자인 (CSS) ---
st.set_page_config(page_title="이경원의 수학연구소", layout="wide")
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #FAFBFC; font-family: 'Pretendard', sans-serif; }
    .white-card { background-color: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 24px; border: 1px solid #F0F2F5; }
    .point-title { font-size: 0.75rem; color: #4A6CF7; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
    h2 { color: #111; font-weight: 800; font-size: 1.8rem; margin-bottom: 0px; }
    .sub-text { color: #666; font-size: 1rem; margin-top: 5px; }
    .notice-text { font-size: 1.05rem; color: #333; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# 주소창에서 id=숫자 읽어오기
sid = st.query_params.get("id")

if sid:
    try:
        # 탭 이름: Student_Master (언더바 확인!)
        df_s = load_data("Student_Master")
        df_s['고유코드'] = df_s['고유코드'].astype(str)
        user = df_s[df_s['고유코드'] == str(sid)]
        
        if not user.empty:
            row = user.iloc[0]
            st.markdown(f"<h2>{row['이름']} 학생 누적 관리 리포트</h2><p class='sub-text'>CLASS : {row['클래스']}</p><br>", unsafe_allow_html=True)
            
            # 강사 리포트 섹션
            comment = row['강사리포트'] if '강사리포트' in row and pd.notna(row['강사리포트']) else "작성된 코멘트가 없습니다."
            st.markdown(f"""
            <div class="white-card">
                <div class="point-title">TEACHER'S REPORT</div>
                <div class="notice-text">{comment}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 그래프 섹션 (Daily_Record 탭에서 데이터 로드)
            df_r = load_data("Daily_Record")
            df_r['이름'] = df_r['이름'].astype(str)
            student_records = df_r[df_r['이름'] == str(row['이름'])].tail(10)
            
            if not student_records.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.bar(student_records, x='날짜', y='테스트점수', text='테스트점수')
                    fig1.update_traces(marker_color='#4A6CF7', textposition='outside')
                    fig1.update_layout(title='<b>최근 테스트 점수</b>', yaxis=dict(range=[0, 115]))
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    fig2 = go.Figure(go.Scatter(x=student_records['날짜'], y=student_records['숙제이행도'], mode='lines+markers+text', text=student_records['숙제이행도'].astype(str) + '%', textposition="top center", line=dict(color='#2ECC71')))
                    fig2.update_layout(title='<b>숙제 이행도 추이</b>', yaxis=dict(range=[0, 115]))
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.error(f"고유코드 [{sid}]를 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    st.title("🛡️ 관리 시스템")
    st.info("URL 뒤에 ?id=고유코드를 입력하세요.")
