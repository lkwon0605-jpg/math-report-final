import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
import datetime
import math

# [설정] 구글 시트 및 API 정보
SHEET_NAME = "이경원의 수학연구소 관리 데이터"

# 새로 발급받은 키 정보를 여기에 직접 입력했습니다.
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "leemathsystem",
    "private_key_id": "a5308230e97880e17ce69b082f43635677916e06",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDNO1ke0RhDas6E\nWT5wHumDJtgqteCkR1CmwkmsbzTZ7QK8PYEs/Tfq7bDgq3GxdZKR141YrnH1ESfn\n8vI24apA9dOzldMC4oKQN5jZdR3blYeyxAsc8wp3kezCz7u/OOBm7b01uKTUseId\nRWaR87+eJIX725CDljYyrn/vkPQOjMzhkLVQNhKysLEh9BgxoWxH4a/kIbAXowOA\nPuf/cBim1B83pfELBaSdtQLEziLpBvUeqGPHVgiHw0VJiCQbwRbprspklz3+JHkk\nkJXwWSdyxBF//RDBKlBu8AiHbWdsmK96v1Hz44CkV6axxmG/hbli7VcICmOuvn2w\nNbIx+GoDAgMBAAECggEAPvx7Zg9TLIGvnwPKu1tpXESELFuEdbajZIKVXNQGeumY\nINCZgAa47iOD2PgVHRsR4Cuw6ColtEpPHos71icc+vHXRrLxP13oJz3A7eBZSQaT\nzoQHSxu2Nys0aDecDdx1VnGZU87224Y6eLRPffS6dt0Lt9fTeucTfCt8/TfWB06X\nbskmkXRm2Zxwuz1ULMhAm+6qPCkbIy0OcXzeF7q4WslPYnPQPuITRhwvqfOtoKGw\niKnL2VSdRgJ4e1nm9ARUIJ+iGcnx4bnezBTiqz5azpRWckHJCgX+dMjVoWYnAxLT\n9+xXPe6zNcVxMwGZPMDYvasujVhuFAj5oT1jTzQjxQKBgQDojQKaKhkEAi7LY5/t\nE7+KEVYHQdoOdQtEEJmusGBd6RCe0O/B8bf+FoGfYYPOI04Wp/sEJKvECyWhWkwM\nJEWivdhUSHRaIAvC2wDBW5A09xw7N9ccBe99jEUgJXwgB98JlP8P8cwfrCZYXim+\nr7mqoWpqcOjQk6bH2UxZGOvtJQKBgQDh7SJxlpOTEiNwtzg04+bktjObG0QBrN/U\nex2TnhPsFJPkI5h5j2Z0dgmwRkkov9nBZS3Ah8JSWiO2/YEJPEDPCrD5qKTYRtln\nYdTUsA9tNHyHzRsgkxlEa4GrvPfIreSPJlWKLXFeYThgadZNqqehfoHOxNL2aIi3\n1CL6j6jWBwKBgGZnKb0vSoK8X1TK0vK33oFy7toVQmtZWROo57PIETdpWRtGUD2s\nLmRiDsRbUYole854PA3wA/85FWH+/DvggRWP2cILgcjqEaPFgoiixFa+dh0RktTR\nPEuhyBLGzujf7|uQuuz6PMF7GFMCW/nTstqqPl+e1PqASVL/uTTNyyPlNAoGAJVIQ\n4IapNiBG7nW1uTb0i0910ud8InK2Ptlfl2UDkXoMvCENLPd9Szu8efwCVdLrW8Ek\n/6rtdMEjKTVTPX1Qj2MKvRMYuAlsHGHS0JeM1NNYxu4gzw69m8nOj9oVbHcdTHBe\nrQa4tYiF0ZdqKUZJjqnhM5Db8IxwGT3X0WAt2b0CgYEA04kJlVqilqzqHs++3hGM\nTjOPAHzebDoJs3N1ysorj6iXLq2vO0FAjEUBdFz7b225IXu1F7aDNEoUrOvSFxVO\n8+Uunw5yIKINbQQ9erPmSNfTNdyDImH/6PB2jWGwfL7tCeKHZes6UHKBi9EvwdT4\nfMvB434K2vJF+P9dP9eiS7o=\n-----END PRIVATE KEY-----\n",
    "client_email": "math-admin@leemathsystem.iam.gserviceaccount.com",
    "client_id": "100893468019480475962",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/math-admin%40leemathsystem.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

@st.cache_data(ttl=600, show_spinner="데이터를 불러오는 중입니다...")
def load_data(tab):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # key.json 파일 대신 SERVICE_ACCOUNT_INFO 변수 사용
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open(SHEET_NAME).worksheet(tab)
    return pd.DataFrame(sh.get_all_records())

# 이하 선생님이 주신 로직(함수 및 디자인) 그대로 유지
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

st.set_page_config(page_title="이경원의 수학연구소", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #FAFBFC; font-family: 'Pretendard', sans-serif; }
    .white-card { background-color: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 24px; border: 1px solid #F0F2F5; }
    .point-title { font-size: 0.75rem; color: #4A6CF7; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
    .point-title-red { color: #FF4B4B; }
    h2 { color: #111; font-weight: 800; letter-spacing: -0.5px; font-size: 1.8rem; margin-bottom: 0px; padding-bottom: 0px;}
    .sub-text { color: #666; font-size: 1rem; margin-top: 5px; }
    .notice-text { font-size: 1.05rem; color: #333; line-height: 1.6; }
    [data-testid="stPlotlyChart"] { background-color: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #F0F2F5; padding: 20px; margin-bottom: 24px; }
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
            
            st.markdown(f"<h2>{name} 학생 누적 관리 리포트</h2><p class='sub-text'>CLASS : {cls}</p><br>", unsafe_allow_html=True)
            
            # Class_Master에서 공지사항 로드
            df_n = load_data("Class_Master")
            note = df_n[df_n['클래스명'] == cls]
            if not note.empty:
                current_week = get_current_week_str()
                html_notice = f"""
<div class="white-card">
<div class="point-title">CLASS NOTICE</div>
<div style="font-size: 1.3rem; font-weight: 700; color:#111; margin-bottom:15px;">{current_week} 주간 안내</div>
<div class="notice-text">
<b>[강의]</b> {note.iloc[0]['이번주 강의']}<br><br>
<b>[과제]</b> {note.iloc[0]['이번주 숙제']}
</div>
</div>
"""
                st.markdown(html_notice, unsafe_allow_html=True)

            # Daily_Record에서 학습 데이터 로드
            df_r = load_data("Daily_Record")
            df_r.columns = df_r.columns.str.replace(' ', '')
            student_records = df_r[df_r['이름'] == name]
            recs = student_records.tail(10)
            
            if not recs.empty:
                recs['날짜'] = recs['날짜'].astype(str)
                recs['test_x_label'] = recs.apply(lambda row: make_label(row['날짜'], row.get('테스트이름', '')), axis=1)
                recs['hw_x_label'] = recs.apply(lambda row: make_label(row['날짜'], row.get('숙제이름', '')), axis=1)
                
                col1, col2 = st.columns(2)
                
                fig1 = px.bar(recs, x='test_x_label', y='테스트점수', text='테스트점수')
                fig1.update_traces(marker_color='#4A6CF7', textposition='outside', width=0.3 if len(recs) <= 3 else None)
                fig1.update_layout(title='<b>최근 10회 테스트 점수</b>', xaxis_title=None, yaxis=dict(range=[0, 115]))
                
                with col1:
                    st.plotly_chart(fig1, use_container_width=True)
                
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=recs['hw_x_label'], y=recs['숙제이행도'], mode='lines+markers+text', text=recs['숙제이행도'].astype(str) + '%', textposition="top center", line=dict(color='#2ECC71')))
                fig2.update_layout(title='<b>최근 10회 숙제 이행도 추이</b>', xaxis_title=None, yaxis=dict(range=[0, 115]))
                
                with col2:
                    st.plotly_chart(fig2, use_container_width=True)

            # 강사 리포트 섹션
            last_comment = user.iloc[0]['강사리포트'] if '강사리포트' in user.columns else "작성된 코멘트가 없습니다."
            html_report = f"""
<div class="white-card">
<div class="point-title">TEACHER'S REPORT</div>
<div class="notice-text">{last_comment}</div>
</div>
"""
            st.markdown(html_report, unsafe_allow_html=True)

        else:
            st.error("학생 정보를 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"데이터 연동 중 오류 발생: {e}")
else:
    st.title("🛡️ 관리자 전용 페이지")
    if st.button("데이터 동기화"):
        st.cache_data.clear()
        st.success("새로고침 완료!")
