import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
from datetime import datetime

# ==========================================
# 1. 환경 설정 및 유틸리티 함수
# ==========================================
st.set_page_config(page_title="NemoStore Senior Analysis Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "nemostore.db")

def format_currency(amount_won):
    """
    금액을 가독성 있게 포맷팅 (원 -> 억/만원)
    왜 중요한가: 투자 의사결정 시 큰 단위의 금액을 빠르게 파악하기 위함
    """
    if amount_won >= 100_000_000:
        uk = amount_won // 100_000_000
        man = (amount_won % 100_000_000) // 10_000
        if man > 0:
            return f"{int(uk)}억 {int(man):,}만원"
        return f"{int(uk)}억원"
    else:
        man = amount_won // 10_000
        return f"{int(man):,}만원"

def format_man_won_simple(amount_won):
    """단순 만원 단위 표기"""
    man = amount_won // 10_000
    return f"{int(man):,}만원"

# ==========================================
# 2. 데이터 엔진 (로드 및 정규화)
# ==========================================
def load_and_process_data():
    if not os.path.exists(DB_PATH):
        st.error("데이터베이스 파일이 존재하지 않습니다.")
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM items", conn)
    finally:
        conn.close()
    
    # 단위 정규화 규칙 적용: 만원 -> 원 (내부 계산용)
    # 데이터베이스 저장값은 '천원' 또는 '만원' 확인 결과 /10 이 '만원'이었으므로 * 10,000 적용
    # data_json_html.md에 따라 필드별 원 단위 변환
    money_fields = ['deposit', 'monthlyRent', 'premium', 'maintenanceFee']
    for field in money_fields:
        if field in df.columns:
            # 값 / 10 = 만원 -> * 10,000 => 원 단위
            df[f'{field}_won'] = (df[field] / 10) * 10_000
            
    # 파생 지표 생성 (의사결정 핵심 지표)
    if all(col in df.columns for col in ['monthlyRent_won', 'maintenanceFee_won']):
        # 1. 월 고정비: 운영 관점의 현금 흐름 파악
        df['monthly_fixed_cost_won'] = df['monthlyRent_won'] + df['maintenanceFee_won']
        
    if all(col in df.columns for col in ['deposit_won', 'premium_won']):
        # 2. 초기 필요 자금: 투자 진입 장벽 파악
        df['initial_investment_won'] = df['deposit_won'] + df['premium_won']
        
    if 'size' in df.columns and df['size'].all() > 0:
        # 3. 면적 대비 비용: 공간 효율성 및 가치 평가
        df['rent_per_m2_won'] = df['monthlyRent_won'] / df['size']
        df['deposit_per_m2_won'] = df['deposit_won'] / df['size']
        
    # 4. 연간 임대비: 장기적 운영 비용 산출
    if 'monthly_fixed_cost_won' in df.columns:
        df['annual_rent_cost_won'] = df['monthly_fixed_cost_won'] * 12
        
    return df

# ==========================================
# 3. UI 컴포넌트 함수
# ==========================================
def render_kpi_cards(data):
    """상단 주요 KPI 카드 렌더링"""
    st.subheader("🚀 핵심 투자 지표 (KPI)")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    # 평균값 기준 시각화
    avg_rent = data['monthlyRent_won'].mean()
    avg_deposit = data['deposit_won'].mean()
    avg_premium = data['premium_won'].mean()
    avg_fixed = data['monthly_fixed_cost_won'].mean()
    avg_invest = data['initial_investment_won'].mean()
    
    c1.metric("평균 월세", format_man_won_simple(avg_rent))
    c2.metric("평균 보증금", format_currency(avg_deposit))
    c3.metric("평균 권리금", format_currency(avg_premium))
    c4.metric("평균 월 고정비", format_man_won_simple(avg_fixed))
    c5.metric("평균 초기 자본", format_currency(avg_invest))

def render_cost_analysis(data):
    """비용 구조 및 효율성 시각화"""
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 초기 투자금 구조")
        # 보증금 vs 권리금 비중 (자산형 vs 소모형 투자 비중 파악)
        labels = ['보증금', '권리금']
        sizes = [data['deposit_won'].mean(), data['premium_won'].mean()]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#66b3ff','#99ff99'])
        ax.axis('equal')
        st.pyplot(fig)
        st.caption("투자 원금 회수가 가능한 '보증금'과 운영 자산인 '권리금'의 비중 비교")

    with col2:
        st.subheader("📉 월 운영 비용 구조")
        # 월세 vs 관리비 비교
        labels = ['순수 월세', '공용 관리비']
        values = [data['monthlyRent_won'].mean(), data['maintenanceFee_won'].mean()]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(labels, [v/10000 for v in values], color=['#ff9999','#ffcc99'])
        ax.set_ylabel("금액 (만원)")
        st.pyplot(fig)
        st.caption("매출 대비 고정 지출 부담을 파악하기 위한 비용 구성")

def render_efficiency_analysis(data):
    """면적 대비 비용 효율성 분석"""
    st.divider()
    st.subheader("📏 면적(㎡) 대비 비용 효율 분석")
    ec1, ec2 = st.columns(2)
    
    with ec1:
        m2_rent = data['rent_per_m2_won'].mean()
        st.metric("㎡당 평균 월세", f"{int(m2_rent):,}원")
        st.caption("단위 면적당 임대 기회 비용")
        
    with ec2:
        m2_deposit = data['deposit_per_m2_won'].mean()
        st.metric("㎡당 평균 보증금", f"{int(m2_deposit):,}원")
        st.caption("단위 면적당 자본 잠김 수준")

# ==========================================
# 4. 메인 실행 루프
# ==========================================
def main():
    st.title("💼 NemoStore Senior Decision Support Dashboard")
    st.markdown("시니어 엔지니어 관점에서 설계된 **실제 데이터 기반 의사결정 지원 도구**입니다.")
    
    df = load_and_process_data()
    
    if df.empty:
        st.warning("데이터를 불러올 수 없습니다.")
        return

    # 사이드바: 전략적 필터링
    st.sidebar.header("🎯 전략 필터")
    region_list = ["전체"] + sorted(df['region'].unique().tolist())
    selected_region = st.sidebar.selectbox("타겟 지역", region_list)
    
    biz_list = ["전체"] + sorted(df['businessMiddleCodeName'].unique().tolist())
    selected_biz = st.sidebar.selectbox("업종 카테고리", biz_list)
    
    # 필터 적용
    filtered_df = df.copy()
    if selected_region != "전체":
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    if selected_biz != "전체":
        filtered_df = filtered_df[filtered_df['businessMiddleCodeName'] == selected_biz]

    # UI 렌더링
    render_kpi_cards(filtered_df)
    render_cost_analysis(filtered_df)
    render_efficiency_analysis(filtered_df)
    
    # 상세 데이터 섹션
    st.divider()
    st.subheader("📽️ 선택 매물 상세 프로필")
    if len(filtered_df) > 0:
        # 가독성을 위해 일부 컬럼만 선택하여 전시
        display_cols = ['title', 'businessMiddleCodeName', 'floor', 'size', 'nearSubwayStation', 
                        'deposit_won', 'monthlyRent_won', 'premium_won', 'initial_investment_won']
        
        # 금액 포맷팅 적용 (UI 전용)
        view_df = filtered_df[display_cols].copy()
        view_df['보증금'] = view_df['deposit_won'].apply(format_currency)
        view_df['월세'] = view_df['monthlyRent_won'].apply(format_man_won_simple)
        view_df['권리금'] = view_df['premium_won'].apply(format_currency)
        view_df['초기자본'] = view_df['initial_investment_won'].apply(format_currency)
        
        st.dataframe(view_df[['title', '보증금', '월세', '권리금', '초기자본', 'size', 'floor', 'nearSubwayStation']], 
                     use_container_width=True)
    else:
        st.info("조건에 일치하는 매물이 없습니다.")

if __name__ == "__main__":
    main()
