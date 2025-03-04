import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import datetime
import plotly.graph_objects as go  # plotly 추가


# --- 페이지 설정 ---
st.set_page_config(page_title="K-water AI Lab 업무 관리 시스템", layout="wide")

# --- 로고 이미지 ---
try:
    im = Image.open("AI_Lab_logo.jpg")  # AI_Lab_logo.jpg 파일이 같은 경로에 있어야 합니다.
    st.sidebar.image(im, caption="K-water AI Lab")  # 이미지와 캡션
except FileNotFoundError:
    st.sidebar.write("Logo image not found.")

# --- 제목 ---
st.title("K-water AI Lab 업무 관리 시스템")

# --- 연구원 정보 (하드코딩, 추후 DB 연동) ---
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

# --- Task 유형 (하드코딩, 설정 페이지에서 관리하도록 개선 가능)---
task_types = ["R&D과제", "내부전문가 과제", "기타 업무지원", "논문", "IP"]


# --- 데이터 저장 (임시: 리스트, 추후 DB 연동) ---
tasks = []

# --- 사이드바 (메뉴) ---
with st.sidebar:
    st.header("메뉴")
    menu = st.radio("선택", ["업무 현황", "업무 추가", "관리자 설정(예정)"])
    # 그래프 및 테이블 표시 여부 체크박스
    show_graph = st.checkbox("현황 그래프 표시", value=True)  # 기본값 True
    show_table = st.checkbox("현황 테이블 표시", value=True)


# --- 업무 현황 페이지 ---
if menu == "업무 현황":
    st.subheader("업무 현황 대시보드")

    # 전체 업무 현황 테이블 (사이드바 체크 여부에 따라 표시)
    if show_table:
        if tasks:
            st.subheader("전체 업무 목록")
            df_tasks = pd.DataFrame(tasks)
            st.dataframe(df_tasks)
        else:
          st.write("등록된 업무가 없습니다.")

    # 개인별 업무 현황 그래프 (사이드바 체크 여부에 따라 표시)
    if show_graph:
      if tasks:
        st.subheader("개인별 업무 현황 그래프")

        # 데이터 준비 (개인별 목표 건수, 진행/완료 건수)
        member_names = list(members.keys())
        target_counts = []  # 개인별 목표 건수
        in_progress_counts = []  # 진행 중 건수
        completed_counts = []  # 완료 건수

        for member in member_names:
          member_tasks = [task for task in tasks if task["담당자"] == member]
          target_counts.append(len(member_tasks)) # 총 개수를 목표로 설정
          in_progress_counts.append(sum(1 for task in member_tasks if task["상태"] == "진행 중"))
          completed_counts.append(sum(1 for task in member_tasks if task["상태"] == "완료"))


        # Plotly 그래프 생성
        fig = go.Figure(data=[
            go.Bar(name='목표', x=member_names, y=target_counts),
            go.Bar(name='진행 중', x=member_names, y=in_progress_counts),
            go.Bar(name='완료', x=member_names, y=completed_counts)
        ])
        # 레이아웃 설정
        fig.update_layout(barmode='group', xaxis_title="연구원", yaxis_title="업무 건수")
        st.plotly_chart(fig)

      else:
          st.write("등록된 업무가 없습니다.")


    # 개인별 업무 현황 테이블 (사이드바 체크와 관계없이 항상 표시)
    st.subheader("개인별 업무 목록")
    if tasks:
      for member in members:
          member_tasks = [task for task in tasks if task["담당자"] == member]
          if member_tasks:
              st.write(f"**{member}**")
              df_member_tasks = pd.DataFrame(member_tasks)[["업무 제목", "업무 유형", "마감일", "상태"]] #필요한 열만 표시
              st.dataframe(df_member_tasks)

    else:
        st.write("등록된 업무가 없습니다.")



# --- 업무 추가 페이지 ---
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
            # 입력값 검증 (필수 입력 항목 확인)
            if not task_name or not assigned_member or not due_date:
                st.error("필수 입력 항목을 모두 채워주세요.")
            else:
                # 데이터 저장
                tasks.append({
                    "업무 제목": task_name,
                    "업무 유형": task_type,
                    "담당자": assigned_member,
                    "마감일": due_date.strftime("%Y-%m-%d"),
                    "상태": task_status,
                    "세부 내용": task_details,
                    "등록일": datetime.date.today().strftime("%Y-%m-%d"),
                })
                st.success("업무가 성공적으로 추가되었습니다.")
                st.experimental_rerun()


# --- 관리자 설정 페이지 (예정) ---
elif menu == "관리자 설정(예정)":
    st.subheader("관리자 설정")
    st.write("추후 개발 예정")


# --- 하단: K-water AI LAB 정보 ---
st.markdown("---")
st.markdown("**K-water AI LAB**")
st.markdown("참여 인력: 김성훈, 이호현, 이충성, 정지영, 김세훈, 정희진, 최영돈, 류제완, 이소령, 김학준, 김용섭, 이아론, 추가채용(예정) (총 13명, 추가 가능)")

