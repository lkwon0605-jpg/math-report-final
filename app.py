import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# [핵심 설정] 깃허브에 올리신 파일 이름과 토씨 하나 안 틀리고 똑같아야 합니다.
SHEET_NAME = "이경원의 수학연구소 관리 데이터"
KEY_FILE = "leemathsystem-a5308230e978.json" 

# 1. 데이터 로드 함수 (파일 직접 읽기 방식)
@st.cache_data(ttl=600)
def load_data(tab_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # 파일을 직접 읽으므로 텍스트 복사 에러(PEM 에러)가 발생하지 않습니다.
        creds = Credentials.from_service_account_file(KEY_FILE, scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open(SHEET_NAME).worksheet(tab_name)
        return pd.DataFrame(sh.get_all_records())
    except Exception as e:
        # 파일명을 못 찾거나 권한이 없을 때 에러를 화면에 띄웁니다.
        st.error(f"연결 오류 발생: {e}")
        return pd.DataFrame()

# --- 리포트 디자인 (선생님의 화이트 카드 양식) ---
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

# URL 주소창의 id 값 확인
sid = st.query_params.get("id")

if sid:
    # 1. 학생 기본 정보 로드 (탭 이름: Student_Master)
    df_s = load_data("Student_Master")
    
    if not df_s.empty:
        # 고유코드를 문자열로 변환하여 매칭 (타입 불일치 방지)
        df_s['고유코드'] = df_s['고유코드'].astype(str)
        user = df_s[df_s['고유코드'] == str(sid)]
        
        if not user.empty:
            row = user.iloc[0]
            st.markdown(f"<h2>{row['이름']} 학생 누적 관리 리포트</h2><p class='sub-text'>CLASS : {row['클래스']}</p><br>", unsafe_allow_html=True)
            
            # 2. 강사 리포트 코멘트 출력
            comment = row['강사리포트'] if '강사리포트' in row and pd.notna(row['강사리포트']) else "이번 주 기록된 코멘트가 없습니다."
            st.markdown(f"""
            <div class="white-card">
                <div class="point-title">TEACHER'S REPORT</div>
                <div class="notice-text">{comment}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 3. 그래프 데이터 로드 (탭 이름: Daily_Record)
            df_r = load_data("Daily_Record")
            if not df_r.empty:
                # 이름 컬럼 공백 제거 및 필터링
                df_r['이름'] = df_r['이름'].astype(str).str.strip()
                student_name = str(row['이름']).strip()
                student_records = df_r[df_r['이름'] == student_name].tail(10)
                
                if not student_records.empty:
                    col1, col2 = st.columns(2)
                    # 테스트 점수 막대 그래프
                    with col1:
                        fig1 = px.bar(student_records, x='날짜', y='테스트점수', text='테스트점수')
                        fig1.update_traces(marker_color='#4A6CF7', textposition='outside')
                        fig1.update_layout(title='<b>최근 테스트 점수</b>', yaxis=dict(range=[0, 115]), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig1, use_container_width=True)
                    # 숙제 이행도 선 그래프
                    with col2:
                        fig2 = go.Figure(go.Scatter(x=student_records['날짜'], y=student_records['숙제이행도'], mode='lines+markers+text', text=student_records['숙제이행도'].astype(str) + '%', textposition="top center", line=dict(color='#2ECC71', width=3)))
                        fig2.update_layout(title='<b>숙제 이행도 추이</b>', yaxis=dict(range=[0, 115]), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning(f"고유코드 [{sid}] 학생을 찾을 수 없습니다. 시트의 데이터를 확인해 주세요.")
    else:
        st.error("시트 데이터를 읽어오지 못했습니다.")
else:
    st.title("🛡️ 학생 관리 시스템")
    st.info("URL 주소창 끝에 ?id=고유코드를 붙여서 접속해 주세요.")
