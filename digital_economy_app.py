import streamlit as st
import pandas as pd
import os
import numpy as np

# Set page config
st.set_page_config(
    page_title="上市公司数字化转型深度洞察系统",
    page_icon="📊",
    layout="wide"
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
                print(f"Loading data from {file_path}...")
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
    # Header
    st.title("DT-Insight 数字化转型指数洞察")
    st.markdown("### 探索企业数字化转型进程")

    # Load Data
    df = load_data()
    
    if df is None or df.empty:
        st.error(f"数据文件未找到或加载失败。请确保 '{CSV_PATH}' 文件位于同一目录下。")
        # Try to show current directory content for debugging
        st.write("当前目录内容:", os.listdir('.'))
        return

    # Search Section
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            search_type = st.selectbox("搜索类型", ["企业名称", "股票代码"])
        with col2:
            query = st.text_input("输入股票代码或简称 (如: 600000 或 浦发银行)")

    if query:
        matched_df = pd.DataFrame()
        if search_type == "股票代码":
            matched_df = df[df['股票代码'] == query]
        else:
            matched_df = df[df['企业名称'] == query]
            if matched_df.empty:
                matched_df = df[df['企业名称'].str.contains(query, na=False)]

        if not matched_df.empty:
            first_code = matched_df['股票代码'].iloc[0]
            company_df = df[df['股票代码'] == first_code].sort_values('年份')
            
            company_name = company_df['企业名称'].iloc[0]
            stock_code = first_code
            
            # Filter years 2000-2023
            company_df = company_df[(company_df['年份'] >= 2000) & (company_df['年份'] <= 2023)]
            
            if company_df.empty:
                st.warning(f"找到企业 {company_name} ({stock_code})，但没有2000-2023年的数据。")
            else:
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
                    dominant_tech = "暂无显著偏好"
                
                total_tech_count = sum(latest_tech_counts.values())

                # Display Info
                st.divider()
                st.header(f"{company_name} ({stock_code})")
                st.caption(f"数据区间: 2000 - 2023 | 最新更新: {latest_year}年")

                # Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("最新转型指数", f"{latest_index}", f"{index_change}")
                m2.metric("平均指数 (24年)", f"{avg_index}")
                m3.metric("核心技术领域", dominant_tech)
                m4.metric("数字技术总频次", f"{int(total_tech_count)}")

                st.divider()

                # Charts
                c1, c2 = st.columns([2, 1])
                
                with c1:
                    st.subheader("数字化转型指数趋势 (2000-2023)")
                    chart_data = company_df.set_index('年份')[['数字化转型指数(0-100分)']]
                    st.line_chart(chart_data)

                with c2:
                    st.subheader(f"技术关注度构成 ({latest_year})")
                    # Prepare data for bar chart
                    tech_data = pd.DataFrame.from_dict(latest_tech_counts, orient='index', columns=['词频'])
                    st.bar_chart(tech_data)

                st.subheader("细分技术词频演变")
                keyword_data = company_df.set_index('年份')[list(tech_cols.keys())]
                # Rename columns for better legend
                keyword_data.columns = list(tech_cols.values())
                st.bar_chart(keyword_data)

                # Data Table
                with st.expander("查看详细数据列表"):
                    display_cols = ['年份', '数字化转型指数(0-100分)', '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数']
                    st.dataframe(company_df[display_cols].sort_values('年份', ascending=False), use_container_width=True)

        else:
            st.error("未找到该企业或股票代码的数据。")

if __name__ == '__main__':
    main()
