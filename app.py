import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# 1. 데이터베이스 설정 (영구 저장)
conn = sqlite3.connect('bean_growth_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS growth_logs
             (group_name TEXT, date TEXT, view_type TEXT, 
              stem_length REAL, leaf_size REAL, photo_path TEXT)''')
conn.commit()

# 앱 제목 및 인터페이스
st.set_page_config(page_title="강낭콩 관찰 AI 튜터", layout="wide")
st.title("🌱 강낭콩 한살이 관찰 기록 시스템")

# 사이드바: 모둠 선택 및 사진 업로드
with st.sidebar:
    st.header("📍 관찰 정보 입력")
    group_name = st.selectbox("우리 모둠 선택", [f"{i}모둠" for i in range(1, 7)])
    view_type = st.radio("촬영 각도", ["정면", "항공샷"])
    stem_len = st.number_input("줄기 길이 (cm)", min_value=0.0, step=0.1)
    leaf_size = st.number_input("잎의 크기 (cm)", min_value=0.0, step=0.1)
    uploaded_file = st.file_uploader("관찰 사진 업로드", type=['jpg', 'png', 'jpeg'])
    
    if st.button("기록 저장하기"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        # 실제 환경에서는 파일을 서버 폴더에 저장하고 경로를 DB에 넣습니다.
        c.execute("INSERT INTO growth_logs VALUES (?, ?, ?, ?, ?, ?)",
                  (group_name, now, view_type, stem_len, leaf_size, "image_path_here"))
        conn.commit()
        st.success(f"{group_name}의 기록이 안전하게 저장되었습니다!")

# 메인 화면: 데이터 시각화 및 AI 튜터
tab1, tab2 = st.tabs(["📊 성장 데이터 확인", "🤖 AI 관찰 튜터"])

with tab1:
    st.subheader(f"🔍 {group_name}의 성장 기록")
    
    # 데이터 불러오기
    df = pd.read_sql_query(f"SELECT * FROM growth_logs WHERE group_name='{group_name}'", conn)
    
    if not df.empty:
        # 그래프 시각화
        fig = px.line(df, x="date", y=["stem_length", "leaf_size"], 
                      title="시간에 따른 줄기 및 잎의 변화",
                      labels={"value": "길이(cm)", "date": "날짜"},
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터 표
        st.write("### 상세 기록표")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("아직 저장된 기록이 없습니다. 사진과 수치를 입력해주세요.")

with tab2:
    st.subheader("💡 AI 관찰 튜터의 한마디")
    if not df.empty:
        latest_data = df.iloc[-1]
        st.info(f"안녕! {group_name} 친구들? 오늘 줄기 길이는 {latest_data['stem_length']}cm구나!")
        
        # AI의 가이드 질문 (로직 기반 간단 구현)
        if len(df) > 1:
            growth_rate = latest_data['stem_length'] - df.iloc[-2]['stem_length']
            if growth_rate > 0:
                st.write(f"지난번보다 **{growth_rate:.1f}cm**나 더 자랐어! 식물이 잘 자라기 위해 너희가 어떤 환경을 만들어줬니?")
            else:
                st.write("성장 속도가 조금 더뎌진 것 같아. 혹시 **햇빛**이 부족하거나 **물**을 너무 많이 주진 않았을까?")
        
        st.text_area("AI 튜터에게 질문하기", placeholder="예: 잎이 노란색으로 변하면 어떻게 해야 하나요?")
        if st.button("조언 듣기"):
            st.write("🤔 강낭콩 잎이 노랗게 변하는 건 대개 물이 너무 많아서 뿌리가 숨을 못 쉴 때 발생해. 화분의 흙을 만져보고 축축하다면 당분간 물주기를 멈춰보는 건 어떨까?")