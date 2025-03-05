import streamlit as st
import pandas as pd
import datetime

# 필수 컬럼 정의
REQUIRED_COLUMNS = ["프로젝트명", "업무명", "담당자", "시작일", "마감일", "상태", "등록일", "업무 유형"]

# tasks.csv 파일 로드 (파일이 없으면 빈 DataFrame 생성)
try:
    tasks_df = pd.read_csv("tasks.csv", encoding='utf-8')
except FileNotFoundError:
    tasks_df = pd.DataFrame(columns=REQUIRED_COLUMNS)


# Streamlit 페이지 설정
st.set_page_config(
    page_title="K-water AI Lab 업무 관리 시스템",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴", ["데이터 조회", "데이터 추가", "데이터 업로드", "관리자 설정(예정)"])

# 메인 화면
st.title("K-water AI Lab 업무 관리 시스템 💧")

if menu == "데이터 조회":
    st.subheader("데이터 조회")
    st.dataframe(tasks_df)

elif menu == "데이터 추가":
    st.subheader("데이터 추가")

    with st.form("task_form"):
        project_name = st.text_input("프로젝트명", placeholder="프로젝트명을 입력하세요.")
        task_name = st.text_input("업무명", placeholder="업무명을 입력하세요.")
        manager = st.text_input("담당자", placeholder="담당자를 입력하세요.")
        start_date = st.date_input("시작일")
        end_date = st.date_input("마감일")
        status = st.selectbox("상태", ["진행 중", "완료", "보류"])
        register_date = datetime.date.today().strftime("%Y-%m-%d")
        task_type = st.selectbox("업무 유형", ["AI 모델 개발", "데이터 분석", "보고서 작성", "회의", "기타 업무지원"])


        submitted = st.form_submit_button("업무 추가")

        if submitted:
            new_task = pd.DataFrame({
                "프로젝트명": [project_name],
                "업무명": [task_name],
                "담당자": [manager],
                "시작일": [start_date],
                "마감일": [end_date],
                "상태": [status],
                "등록일": [register_date],
                "업무 유형": [task_type]
            })
            tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
            tasks_df.to_csv("tasks.csv", index=False, encoding='utf-8')
            st.success("업무가 성공적으로 추가되었습니다.")
            st.experimental_rerun() # 데이터 추가 후 페이지 새로고침


elif menu == "데이터 업로드":
    st.subheader("데이터 업로드")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file, encoding='utf-8')

            # 누락된 컬럼 처리 및 기본값 설정
            for col in REQUIRED_COLUMNS:
                if col not in uploaded_df.columns:
                    if col == "업무 유형":
                        uploaded_df[col] = "기타 업무지원"
                    elif col == "마감일":
                        uploaded_df[col] = "2024-06-30"  # 기본 마감일
                    elif col == "상태":
                        uploaded_df[col] = "진행 중"  # 기본 상태
                    elif col == "등록일":
                        uploaded_df[col] = datetime.date.today().strftime("%Y-%m-%d") #오늘 날짜
                    else:
                        uploaded_df[col] = ""  # 기타 컬럼은 빈 문자열

            overwrite = st.selectbox("데이터 처리 방법", ["기존 데이터에 추가", "기존 데이터 덮어쓰기"])

            if st.button("데이터 업로드"):
                if overwrite == "기존 데이터에 추가":
                    tasks_df = pd.concat([tasks_df, uploaded_df[REQUIRED_COLUMNS]], ignore_index=True)
                else:
                    tasks_df = uploaded_df[REQUIRED_COLUMNS]

                tasks_df.to_csv("tasks.csv", index=False, encoding='utf-8')
                st.success("데이터가 성공적으로 업로드되었습니다. (Github에는 수동 업로드 필요)")

        except Exception as e:
            st.error(f"파일 업로드 중 오류 발생: {e}")

elif menu == "관리자 설정(예정)":
    st.subheader("관리자 설정")
    st.write("추후 개발 예정")

st.markdown("---")
st.markdown("**K-water AI LAB**")
st.markdown(
    "참여 인력: 김성훈, 이호현, 이충성, 정지영, 김세훈, 정희진, 최영돈, 류제완, 이소령, 김학준, 김용섭, 이아론, 추가채용(예정) (총 13명, 추가 가능)"
)
