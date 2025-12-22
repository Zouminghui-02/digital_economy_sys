import streamlit as st
import pandas as pd
import os
import numpy as np

# Set page config
st.set_page_config(
    page_title="上市公司数字化转型深度洞察系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
CSV_PATH = r'1999-2023年数字化转型指数结果表.csv'

# Load data function
@st.cache_data
def load_data():
    if os.path.exists(CSV_PATH):
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, CSV_PATH)
            
            # If relative path fails, try absolute path if CSV_PATH was already absolute or relative to cwd
            if not os.path.exists(file_path):
                file_path = CSV_PATH
                
            if os.path.exists(file_path):
                # print(f"Loading data from {file_path}...")
                df = pd.read_csv(file_path, encoding='utf-8', dtype={'股票代码': str})
                df['年份'] = pd.to_numeric(df['年份'], errors='coerce')
                
                # Ensure numeric columns for metrics
                metric_cols = ['数字化转型指数(0-100分)', '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数', '数字技术运用词频数']
                for col in metric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                return df
            else:
                 return None
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    else:
        # Check in current working directory as fallback
        if os.path.exists(CSV_PATH):
             try:
                df = pd.read_csv(CSV_PATH, encoding='utf-8', dtype={'股票代码': str})
                df['年份'] = pd.to_numeric(df['年份'], errors='coerce')
                # Ensure numeric columns for metrics
                metric_cols = ['数字化转型指数(0-100分)', '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数', '数字技术运用词频数']
                for col in metric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                return df
             except Exception as e:
                st.error(f"Error loading CSV: {e}")
                return pd.DataFrame()
        return None

# Main App
def main():
    # Sidebar Search
    with st.sidebar:
        st.title("🔍 搜索配置")
        st.markdown("---")
        
        # Load Data
        df = load_data()
        
        if df is None or df.empty:
            st.error(f"⚠️ 数据文件加载失败。\n请检查 '{CSV_PATH}' 是否存在。")
            st.stop()
            
        search_type = st.radio("选择搜索方式", ["企业名称", "股票代码"], horizontal=True)
        query = st.text_input("请输入关键词", placeholder="例如: 600000 或 浦发银行")
        
        st.markdown("---")
        st.markdown("### ℹ️ 关于系统")
        st.info("本系统旨在展示上市公司在数字化转型方面的投入与成效。数据涵盖1999-2023年。")
        st.caption("Data Source: 1999-2023年数字化转型指数")

    # Main Content Area
    st.title("📈 DT-Insight 数字化转型指数洞察")
    
    if not query:
        st.container()
        st.info("👈 请在左侧侧边栏输入 **股票代码** 或 **企业名称** 开始探索。")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 📊 多维指标")
            st.caption("查看企业数字化转型指数及历年变化趋势。")
        with col2:
            st.markdown("### 🧠 技术洞察")
            st.caption("分析人工智能、大数据、云计算等核心技术领域的投入偏好。")
        with col3:
            st.markdown("### 📅 历史回溯")
            st.caption("完整覆盖1999至2023年长周期数据。")
        
        st.divider()
        st.markdown("#### 💡 热门搜索示例")
        st.code("600000 (浦发银行)", language="text")
        st.code("600519 (贵州茅台)", language="text")
        return

    # Search Logic
    matched_df = pd.DataFrame()
    if search_type == "股票代码":
        matched_df = df[df['股票代码'] == query]
    else:
        matched_df = df[df['企业名称'] == query]
        if matched_df.empty:
            matched_df = df[df['企业名称'].str.contains(query, na=False)]

    if matched_df.empty:
        st.warning(f"⚠️ 未找到匹配项: '{query}'")
        st.markdown("### 建议")
        st.markdown("- 检查输入的股票代码是否正确")
        st.markdown("- 尝试使用企业简称进行模糊搜索")
        return

    # Process matched data
    first_code = matched_df['股票代码'].iloc[0]
    company_df = df[df['股票代码'] == first_code].sort_values('年份')
    company_name = company_df['企业名称'].iloc[0]
    stock_code = first_code
    
    # Filter years
    company_df = company_df[(company_df['年份'] >= 1999) & (company_df['年份'] <= 2023)]
    
    if company_df.empty:
        st.warning(f"⚠️ 找到企业 {company_name} ({stock_code})，但缺乏1999-2023年的有效数据。")
        return

    # Calculate stats
    latest_row = company_df.iloc[-1]
    latest_year = int(latest_row['年份'])
    latest_index = latest_row['数字化转型指数(0-100分)']
    
    avg_index = round(company_df['数字化转型指数(0-100分)'].mean(), 2)
    
    index_change = 0
    if len(company_df) >= 2:
        prev_index = company_df.iloc[-2]['数字化转型指数(0-100分)']
        index_change = round(latest_index - prev_index, 2)
    
    # Dominant Tech
    tech_cols = {'人工智能词频数': '人工智能', '大数据词频数': '大数据', '云计算词频数': '云计算', '区块链词频数': '区块链'}
    latest_tech_counts = {name: latest_row.get(col, 0) for col, name in tech_cols.items()}
    dominant_tech = max(latest_tech_counts, key=latest_tech_counts.get)
    if latest_tech_counts[dominant_tech] == 0:
        dominant_tech = "均衡/无偏好"
    
    total_tech_count = sum(latest_tech_counts.values())

    # Dashboard Header
    st.markdown("---")
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.subheader(f"🏢 {company_name}")
        st.caption(f"股票代码: {stock_code} | 数据截止: {latest_year}年")
    with header_col2:
        st.markdown(f"<div style='text-align: right; color: gray; padding-top: 10px;'>数据跨度: {len(company_df)} 年</div>", unsafe_allow_html=True)

    # Key Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🚀 最新转型指数", f"{latest_index}", f"{index_change}", delta_color="normal")
    m2.metric("📈 24年平均指数", f"{avg_index}")
    m3.metric("🔥 核心技术领域", dominant_tech)
    m4.metric("∑ 数字技术总词频", f"{int(total_tech_count)}")

    st.markdown("---")

    # Tabs for Content
    tab1, tab2, tab3 = st.tabs(["📊 趋势分析", "🧩 技术构成", "📋 详细数据"])

    with tab1:
        st.markdown("#### 数字化转型指数走势 (1999-2023)")
        chart_data = company_df.set_index('年份')[['数字化转型指数(0-100分)']]
        st.line_chart(chart_data)
        
        st.markdown("#### 细分技术词频演变")
        keyword_data = company_df.set_index('年份')[list(tech_cols.keys())]
        keyword_data.columns = list(tech_cols.values())
        st.area_chart(keyword_data)

    with tab2:
        st.markdown(f"#### {latest_year}年技术关注度构成")
        col_a, col_b = st.columns([2, 1])
        with col_a:
            tech_data = pd.DataFrame.from_dict(latest_tech_counts, orient='index', columns=['词频'])
            tech_data = tech_data.sort_values('词频', ascending=True)
            st.bar_chart(tech_data, horizontal=True)
        with col_b:
             st.info("💡 说明：\n该图表展示了企业在最近一年财报中各数字技术关键词的出现频率分布，反映了企业当前的技术投入重点。")

    with tab3:
        st.markdown("#### 年度详细数据表")
        display_cols = ['年份', '数字化转型指数(0-100分)', '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数']
        
        # Styling dataframe if possible, otherwise just display
        df_display = company_df[display_cols].sort_values('年份', ascending=False)
        st.dataframe(
            df_display,
            column_config={
                "年份": st.column_config.NumberColumn(format="%d"),
                "数字化转型指数(0-100分)": st.column_config.NumberColumn(format="%.2f"),
            },
            use_container_width=True,
            hide_index=True
        )

if __name__ == '__main__':
    main()
