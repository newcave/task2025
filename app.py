import streamlit as st
import pandas as pd
from PIL import Image
import datetime
import plotly.graph_objects as go
import os
import io
import subprocess
import requests

# --- GitHub Repository Information ---
GITHUB_REPO_OWNER = "newcave"  # GitHub 사용자 이름
GITHUB_REPO_NAME = "task2025"  # GitHub 저장소 이름
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}"
GITHUB_TOKEN = "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"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # Streamlit Secrets에서 GitHub 토큰 가져오기
DATA_FILE = "tasks.csv"
REQUIRED_COLUMNS = ["업무 제목", "업무 유형", "담당자", "마감일", "상태", "세부 내용", "등록일"]

# --- Page Config ---
st.set_page_config(page_title="K-water AI Lab 업무 관리 Tool", layout="wide")

# --- Logo (Simplified) ---
logo_path = "AI_Lab_logo.jpg"  # 실제 이미지 파일 경로
if os.path.exists(logo_path):
    im = Image.open(logo_path)
    st.sidebar.image(im, caption="K-water AI Lab")
else:
    st.sidebar.write("Logo image not found.")

# --- Title ---
st.title("K-water AI Lab 업무 관리 시스템")

# --- Members and Task Types ---
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


# --- Data Loading Function (from GitHub) ---
def load_data_from_github():
    """GitHub 저장소에서 CSV 파일을 불러옵니다."""
    try:
        url = f"https://raw.githubusercontent.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/main/{DATA_FILE}"
        df = pd.read_csv(url, encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"GitHub에서 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

# --- Data Saving Function (to GitHub) ---
def save_data_to_github(df, commit_message="Update data"):
    """데이터프레임을 CSV 파일로 변환하고 GitHub 저장소에 커밋합니다. (HTTPS, subprocess 사용)"""
    try:
        # CSV 파일로 변환
        csv_data = df.to_csv(index=False, encoding='utf-8')

        # 로컬 임시 디렉토리에 저장소 클론 (또는 기존 저장소 사용)
        repo_dir = "/tmp/task2025_repo"
        if not os.path.exists(repo_dir):
            # HTTPS URL로 클론
            subprocess.run(["git", "clone", GITHUB_REPO_URL, repo_dir], check=True, capture_output=True, text=True)
        else:
            # 기존 저장소 pull
             subprocess.run(["git", "-C", repo_dir, "pull"], check=True, capture_output=True, text=True)

        # CSV 파일 쓰기
        file_path = os.path.join(repo_dir, DATA_FILE)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(csv_data)

        # Git 명령어 실행 (subprocess)
        commands = [
            ["git", "-C", repo_dir, "config", "user.email", "your_email@example.com"],  # 실제 이메일
            ["git", "-C", repo_dir, "config", "user.name", "Your Name"],  # 실제 이름
            ["git", "-C", repo_dir, "add", DATA_FILE],
            ["git", "-C", repo_dir, "commit", "-m", commit_message],
            # HTTPS URL과 토큰을 사용한 push, --porcelain 제거, origin 추가
            ["git", "-C", repo_dir, "push", f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}.git", "main"],
        ]

        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            st.write(f"Executing command: {cmd}, Result: {result}") # 디버깅
            if result.returncode != 0:
                st.error(f"Git 명령어 실행 중 오류 발생: {result.stderr}")
                return False

        return True

    except Exception as e:
        st.error(f"GitHub에 데이터 저장 중 오류 발생: {e}")
        return False



# --- Data Loading ---
# 초기 데이터 로드 (앱 시작 시)
tasks_df = load_data_from_github()


# --- Sidebar ---
with st.sidebar:
    st.header("메뉴")
    menu = st.radio("선택", ["업무 현황", "업무 추가", "데이터 업로드", "GitHub 저장", "관리자 설정(예정)"])
    show_graph = st.checkbox("현황 그래프 표시", value=True)
    show_table = st.checkbox("현황 테이블 표시", value=True)

    # CSV Download Button
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
                st.dataframe(member_tasks_df[REQUIRED_COLUMNS])
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
                # DataFrame에 새 업무 추가
                tasks_df = pd.concat([tasks_df, pd.DataFrame([new_task])], ignore_index=True)

                # GitHub에 저장
                if save_data_to_github(tasks_df):
                    st.success("업무가 성공적으로 추가되었으며, GitHub에 저장되었습니다.")
                    # GitHub에서 데이터 다시 불러오기 (즉시 반영)
                    tasks_df = load_data_from_github()
                    st.rerun()  # 데이터 로드 후, 화면 갱신

                else:
                    st.error("GitHub 저장에 실패했습니다.")


elif menu == "데이터 업로드":
    st.subheader("데이터 업로드")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file, encoding='utf-8')

            for col in REQUIRED_COLUMNS:
                if col not in uploaded_df.columns:
                    if col == "업무 유형":
                        uploaded_df[col] = "기타 업무지원"
                    elif col == "마감일":
                        uploaded_df[col] = "2024-06-30"
                    elif col == "상태":
                        uploaded_df[col] = "진행 중"
                    elif col == "등록일":
                        uploaded_df[col] = datetime.date.today().strftime("%Y-%m-%d")
                    else:
                        uploaded_df[col] = ""

            overwrite = st.selectbox("데이터 처리 방법", ["기존 데이터에 추가", "기존 데이터 덮어쓰기"])

            if st.button("데이터 업로드"):
                if overwrite == "기존 데이터에 추가":
                    tasks_df = pd.concat([tasks_df, uploaded_df[REQUIRED_COLUMNS]], ignore_index=True)
                else:
                    tasks_df = uploaded_df[REQUIRED_COLUMNS]

                if save_data_to_github(tasks_df):
                    st.success("데이터가 성공적으로 업로드되었으며, GitHub에 저장되었습니다.")
                    # GitHub에서 데이터 다시 불러오기 (즉시 반영)
                    tasks_df = load_data_from_github()
                    st.rerun()

                else:
                    st.error("GitHub 저장에 실패했습니다.")

        except Exception as e:
            st.error(f"파일 업로드 중 오류 발생: {e}")

elif menu == "GitHub 저장":
    st.subheader("GitHub 저장")
    commit_message = st.text_input("커밋 메시지", "Update data from Streamlit app")
    if st.button("GitHub에 저장"):
        if save_data_to_github(tasks_df, commit_message):
            st.success("데이터가 GitHub에 성공적으로 저장되었습니다.")
            # GitHub에서 데이터 다시 불러오기 (즉시 반영)
            tasks_df = load_data_from_github()
            st.rerun()

        else:
            st.error("GitHub 저장에 실패했습니다.")

elif menu == "관리자 설정(예정)":
    st.subheader("관리자 설정")
    st.write("추후 개발 예정")

st.markdown("---")
st.markdown("**K-water AI LAB**")
st.markdown(
    "참여 인력: 김성훈, 이호현, 이충성, 정지영, 김세훈, 정희진, 최영돈, 류제완, 이소령, 김학준, 김용섭, 이아론, 추가채용(예정) (총 13명, 추가 가능)"
)
