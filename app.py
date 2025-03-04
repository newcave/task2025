import streamlit as st
import pandas as pd
from PIL import Image
import datetime
import plotly.graph_objects as go
import os
import io  # Import the io module


# --- Page Config ---
st.set_page_config(page_title="K-water AI Lab 업무 관리 Tool", layout="wide")

# --- Logo (Simplified) ---
logo_path = "AI_Lab_logo.jpg"
if os.path.exists(logo_path):
    im = Image.open(logo_path)
    st.sidebar.image(im, caption="K-water AI Lab")
else:
    st.sidebar.write("Logo image not found.")

# --- Title ---
st.title("K-water AI Lab 업무 관리 시스템")

# --- Members and Task Types (Consider using a config file later) ---
members = {
    "김성훈": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "이호현": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "이충성": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "정지영": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "김세훈": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "정희진": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "최영돈": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "류제완": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "이소령": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "김학준": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "김용섭": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "이아론": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
    "추가채용(예정)": ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"],
}

task_types = ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"]

# --- Data Loading (CSV) ---
DATA_FILE = "tasks.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, encoding='utf-8')  # UTF-8 인코딩 명시
    else:
        return pd.DataFrame()

tasks_df = load_data()


# --- Sidebar ---
with st.sidebar:
    st.header("메뉴")
    menu = st.radio("선택", ["업무 현황", "업무 추가", "데이터 업로드", "관리자 설정(예정)"])
    show_graph = st.checkbox("현황 그래프 표시", value=True)
    show_table = st.checkbox("현황 테이블 표시", value=True)

    # CSV Download Button (in the sidebar)
    if not tasks_df.empty:
        csv = tasks_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name='kwater_tasks.csv',
            mime='text/csv',
        )


# --- Main Content ---

if menu == "업무 현황":
    st.subheader("업무 현황 대시보드")

    if show_table and not tasks_df.empty:
        st.subheader("전체 업무 목록")
        st.dataframe(tasks_df)
    elif show_table:
        st.write("등록된 업무가 없습니다.")

    if show_graph and not tasks_df.empty:
        st.subheader("개인별 업무 현황 그래프")

        member_names = list(members.keys())
        target_counts = []
        in_progress_counts = []
        completed_counts = []

        for member in member_names:
            member_tasks = tasks_df[tasks_df["담당자"] == member]
            target_counts.append(len(member_tasks))
            in_progress_counts.append(member_tasks[member_tasks["상태"] == "진행 중"].shape[0])
            completed_counts.append(member_tasks[member_tasks["상태"] == "완료"].shape[0])

        fig = go.Figure(
            data=[
                go.Bar(name="목표", x=member_names, y=target_counts),
                go.Bar(name="진행 중", x=member_names, y=in_progress_counts),
                go.Bar(name="완료", x=member_names, y=completed_counts),
            ]
        )
        fig.update_layout(barmode="group", xaxis_title="연구원", yaxis_title="업무 건수")
        st.plotly_chart(fig)

    elif show_graph:
        st.write("등록된 업무가 없습니다.")

    st.subheader("개인별 업무 목록")
    if not tasks_df.empty:
        for member in members:
            member_tasks_df = tasks_df[tasks_df["담당자"] == member]
            if not member_tasks_df.empty:
                st.write(f"**{member}**")
                st.dataframe(member_tasks_df[["업무 제목", "업무 유형", "마감일", "상태"]])
    else:
        st.write("등록된 업무가 없습니다.")

elif menu == "업무 추가":
    st.subheader("신규 업무 등록")

    with st.form("task_form"):
        task_name = st.text_input("업무 제목", max_chars=100)
        task_type = st.selectbox("업무 유형", task_types)
        assigned_member = st.selectbox("담당자", list(members.keys()))
        due_date = st.date_input("마감일")
        task_status = st.selectbox("상태", ["진행 중", "대기 중", "완료"])
        task_details = st.text_area("세부 내용", height=150)

        submitted = st.form_submit_button("업무 추가")
        if submitted:
            if not task_name or not assigned_member or not due_date:
                st.error("필수 입력 항목을 모두 채워주세요.")
            else:
                new_task = {
                    "업무 제목": task_name,
                    "업무 유형": task_type,
                    "담당자": assigned_member,
                    "마감일": due_date.strftime("%Y-%m-%d"),
                    "상태": task_status,
                    "세부 내용": task_details,
                    "등록일": datetime.date.today().strftime("%Y-%m-%d"),
                }

                tasks_df = pd.concat([tasks_df, pd.DataFrame([new_task])], ignore_index=True)
                tasks_df.to_csv(DATA_FILE, index=False)
                st.success("업무가 성공적으로 추가되었습니다.")

elif menu == "데이터 업로드":
    st.subheader("데이터 업로드")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file is not None:
        try:
            # Read the uploaded CSV file
            uploaded_df = pd.read_csv(uploaded_file, encoding='utf-8') # UTF-8 인코딩 명시

            # Validate the uploaded file (check for required columns)
            required_columns = ["업무 제목", "업무 유형", "담당자", "마감일", "상태", "세부 내용", "등록일"]
            if not all(col in uploaded_df.columns for col in required_columns):
                st.error(f"업로드된 파일에 필요한 컬럼이 없습니다. 다음 컬럼들이 필요합니다: {', '.join(required_columns)}")
            else:
                # Confirm overwrite with a selectbox
                overwrite = st.selectbox("데이터 처리 방법", ["기존 데이터에 추가", "기존 데이터 덮어쓰기"])

                if st.button("데이터 업로드"):
                    if overwrite == "기존 데이터에 추가":
                         # Append the uploaded data to the existing data
                        tasks_df = pd.concat([tasks_df, uploaded_df], ignore_index=True)
                    else: # "기존 데이터 덮어쓰기"
                        # Overwrite the existing data with the uploaded data
                        tasks_df = uploaded_df

                    # Save the updated DataFrame to the CSV file
                    tasks_df.to_csv(DATA_FILE, index=False)
                    st.success("데이터가 성공적으로 업로드되었습니다.")

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
