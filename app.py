import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import plotly.graph_objects as go
import datetime
import math

# 💡 [핵심] 이 설정이 무조건 코드의 첫 번째 스트림릿 명령어야 에러가 안 납니다!
st.set_page_config(page_title="이경원의 수학연구소", layout="wide")

# [설정] 구글 시트 이름
SHEET_NAME = "이경원의 수학연구소 관리 데이터" 

@st.cache_data(ttl=600, show_spinner="데이터를 불러오는 중입니다...")
def load_data(tab):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    client = gspread.authorize(creds)
    sh = client.open(SHEET_NAME).worksheet(tab)
    return pd.DataFrame(sh.get_all_records())

def get_current_week_str():
    today = datetime.datetime.now()
    month = today.month
    first_day = today.replace(day=1)
    adjusted_dom = today.day + first_day.weekday()
    week_num = int(math.ceil(adjusted_dom / 7.0))
    return f"{month}월 {week_num}주차"

def make_label(date, name):
    name_str = str(name).strip()
    if name_str and name_str.lower() != 'nan':
        return f"{date}<br>{name_str}"
    return str(date)

# CSS 스타일 적용
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #FAFBFC; font-family: 'Pretendard', sans-serif; }
    .white-card { background-color: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 20px; border: 1px solid #F0F2F5; }
    .point-title { font-size: 0.75rem; color: #4A6CF7; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
    .point-title-red { color: #FF4B4B; }
    h2 { color: #111; font-weight: 800; letter-spacing: -0.5px; font-size: 1.8rem; margin-bottom: 5px; }
    .sub-text { color: #666; font-size: 1rem; margin-bottom: 20px; }
    .notice-text { font-size: 1.05rem; color: #333; line-height: 1.6; }
    [data-testid="stPlotlyChart"] { background-color: white; border-radius: 16px; border: 1px solid #F0F2F5; padding: 10px; }
</style>
""", unsafe_allow_html=True)

sid = st.query_params.get("id")

if sid:
    try:
        df_s = load_data("Student_Master")
        df_s.columns = df_s.columns.str.replace(' ', '')
        user = df_s[df_s['고유코드'].astype(str) == str(sid)]
        
        if not user.empty:
            name = user.iloc[0]['이름']
            cls = user.iloc[0]['클래스']
            st.markdown(f"<h2>{name} 학생 누적 관리 리포트</h2><div class='sub-text'>CLASS : {cls}</div>", unsafe_allow_html=True)
            
            # 주간 안내
            df_n = load_data("Class_Master")
            note = df_n[df_n['클래스명'] == cls]
            if not note.empty:
                current_week = get_current_week_str()
                st.markdown(f"""
                <div class="white-card">
                    <div class="point-title">CLASS NOTICE</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color:#111; margin-bottom:10px;">{current_week} 주간 안내</div>
                    <div class="notice-text"><b>[강의]</b> {note.iloc[0]['이번주 강의']}<br><b>[과제]</b> {note.iloc[0]['이번주 숙제']}</div>
                </div>
                """, unsafe_allow_html=True)

            # 기록 데이터
            df_r = load_data("Daily_Record")
            df_r.columns = df_r.columns.str.replace(' ', '')
            student_records = df_r[df_r['이름'] == name]
            recs = student_records.tail(10)
            
            if not recs.empty:
                recs['날짜'] = recs['날짜'].astype(str)
                recs['test_x'] = recs.apply(lambda r: make_label(r['날짜'], r.get('테스트이름', '')), axis=1)
                recs['hw_x'] = recs.apply(lambda r: make_label(r['날짜'], r.get('숙제이름', '')), axis=1)
                
                c1, c2 = st.columns(2)
                with c1:
                    fig1 = px.bar(recs, x='test_x', y='테스트점수', text='테스트점수', title="<b>최근 10회 테스트 점수</b>")
                    fig1.update_traces(marker_color='#4A6CF7', width=0.3, textposition='outside')
                    fig1.update_layout(xaxis_title=None, yaxis=dict(range=[0, 110]), height=350, margin=dict(l=10, r=10, t=50, b=40))
                    st.plotly_chart(fig1, use_container_width=True)
                with c2:
                    fig2 = px.line(recs, x='hw_x', y='숙제이행도', markers=True, title="<b>최근 10회 숙제 이행도 추이</b>")
                    fig2.update_traces(line_color='#2ECC71', marker=dict(size=8, color='white', line=dict(width=2, color='#2ECC71')))
                    fig2.update_layout(xaxis_title=None, yaxis=dict(range=[0, 110]), height=350, margin=dict(l=10, r=10, t=50, b=40))
                    st.plotly_chart(fig2, use_container_width=True)

                if '취약유형' in student_records.columns:
                    w_list = student_records['취약유형'].dropna().astype(str).str.strip()
                    w_list = w_list[w_list != ""].unique()[-5:]
                    if len(w_list) > 0:
                        items = "".join([f"<li>{w}</li>" for w in w_list])
                        st.markdown(f"""
                        <div class="white-card">
                            <div class="point-title point-title-red">FOCUS AREA</div>
                            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom:10px;">누적 취약 유형 점검</div>
                            <ul style="margin:0; padding-left:20px;">{items}</ul>
                        </div>
                        """, unsafe_allow_html=True)

            last_comment = user.iloc[0].get('강사리포트', '이번 주 리포트가 아직 등록되지 않았습니다.')
            st.markdown(f"""
            <div class="white-card">
                <div class="point-title">TEACHER'S REPORT</div>
                <div class="notice-text">{last_comment}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("학생 정보를 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"데이터 연동 중 오류가 발생했습니다. (상세: {e})")
else:
    st.title("🛡️ 관리자 전용 페이지")
    if st.button("데이터 동기화 (새로고침)"):
        st.cache_data.clear()
        st.success("최신 데이터로 갱신되었습니다.")