from flask import Flask, request, render_template_string
import pandas as pd
import json
import os
import numpy as np

app = Flask(__name__)

# Configuration
CSV_PATH = r'1999-2023年数字化转型指数结果表.csv'
# Using a professional color palette
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'accent': '#e74c3c',
    'background': '#f4f6f9',
    'card_bg': '#ffffff',
    'text': '#2c3e50',
    'text_light': '#7f8c8d'
}

# Load data globally
try:
    if os.path.exists(CSV_PATH):
        print(f"Loading data from {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH, encoding='utf-8', dtype={'股票代码': str})
        df['年份'] = pd.to_numeric(df['年份'], errors='coerce')
        # Ensure numeric columns for metrics
        metric_cols = ['数字化转型指数(0-100分)', '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数', '数字技术运用词频数']
        for col in metric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    else:
        print(f"Error: File not found at {CSV_PATH}")
        df = pd.DataFrame()
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上市公司数字化转型深度洞察系统</title>
    <!-- ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <!-- Tailwind CSS for rapid modern styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        body { font-family: 'Inter', system-ui, -apple-system, sans-serif; background-color: #f4f6f9; color: #334155; }
        .glass-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .glass-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .gradient-text {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .search-input:focus {
            ring: 2px solid #3b82f6;
            outline: none;
        }
    </style>
    <script>
        function quickSearch(val, type) {
            const form = document.querySelector('form');
            form.querySelector('input[name="query"]').value = val;
            form.querySelector('select[name="search_type"]').value = type;
            form.submit();
        }
    </script>
</head>
<body class="min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">D</div>
                    <span class="text-xl font-bold text-slate-800">DT-Insight <span class="text-xs font-normal text-slate-500 ml-1">数字化转型指数洞察</span></span>
                </div>

            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 py-8 max-w-7xl">
        
        <!-- Search Section -->
        <div class="max-w-3xl mx-auto mb-12 text-center">
            <h1 class="text-3xl font-bold mb-6 text-slate-800">探索企业数字化转型进程</h1>
            <form method="POST" class="relative max-w-xl mx-auto">
                <div class="flex shadow-lg rounded-full overflow-hidden border border-slate-200 bg-white p-1">
                    <select name="search_type" class="bg-transparent pl-4 pr-2 py-3 text-sm font-medium text-slate-600 focus:outline-none border-r border-slate-100 cursor-pointer hover:bg-slate-50 rounded-l-full transition-colors">
                        <option value="name" {% if search_type == 'name' %}selected{% endif %}>企业名称</option>
                        <option value="code" {% if search_type == 'code' %}selected{% endif %}>股票代码</option>
                    </select>
                    <input type="text" name="query" value="{{ query }}" placeholder="输入股票代码或简称 (如: 600000 或 浦发银行)" 
                           class="flex-grow px-4 py-3 text-slate-700 placeholder-slate-400 focus:outline-none" required>
                    <button type="submit" class="bg-blue-600 text-white px-8 py-3 rounded-full font-medium hover:bg-blue-700 transition-colors flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        查询
                    </button>
                </div>
            </form>
            <div class="mt-4 flex justify-center gap-4 text-sm text-slate-500">
                <span>热门搜索:</span>
                <a href="#" onclick="quickSearch('平安银行', 'name')" class="hover:text-blue-600 underline decoration-dotted">平安银行</a>
                <a href="#" onclick="quickSearch('600519', 'code')" class="hover:text-blue-600 underline decoration-dotted">贵州茅台</a>
                <a href="#" onclick="quickSearch('美的集团', 'name')" class="hover:text-blue-600 underline decoration-dotted">美的集团</a>
            </div>
        </div>

        {% if error %}
            <div class="max-w-2xl mx-auto bg-red-50 border-l-4 border-red-500 p-4 rounded-r shadow-sm mb-8">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700">{{ error }}</p>
                    </div>
                </div>
            </div>
        {% endif %}

        {% if company_name %}
        <!-- Dashboard Content -->
        <div class="animate-fade-in-up">
            <!-- Header Info -->
            <div class="flex items-end justify-between mb-8 border-b border-slate-200 pb-4">
                <div>
                    <h2 class="text-3xl font-bold text-slate-800">{{ company_name }} <span class="text-xl font-normal text-slate-500 ml-2">({{ stock_code }})</span></h2>
                    <p class="text-slate-500 mt-1">数据区间: 2000 - 2023</p>
                </div>
                <div class="text-right">
                    <div class="text-sm text-slate-500">最新更新</div>
                    <div class="text-lg font-semibold text-slate-700">{{ latest_year }}年</div>
                </div>
            </div>

            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="glass-card p-6 border-t-4 border-blue-500">
                    <div class="text-sm font-medium text-slate-500 uppercase tracking-wider mb-1">最新转型指数</div>
                    <div class="flex items-baseline">
                        <span class="text-4xl font-bold text-slate-800">{{ latest_index }}</span>
                        <span class="ml-2 text-sm text-slate-400">/ 100</span>
                    </div>
                    <div class="mt-2 text-sm {{ 'text-green-600' if index_change >= 0 else 'text-red-600' }}">
                        {{ '▲' if index_change >= 0 else '▼' }} {{ index_change }} (较上年)
                    </div>
                </div>
                
                <div class="glass-card p-6 border-t-4 border-indigo-500">
                    <div class="text-sm font-medium text-slate-500 uppercase tracking-wider mb-1">平均指数 (24年)</div>
                    <div class="text-4xl font-bold text-slate-800">{{ avg_index }}</div>
                    <div class="mt-2 text-sm text-slate-500">长期表现</div>
                </div>

                <div class="glass-card p-6 border-t-4 border-purple-500">
                    <div class="text-sm font-medium text-slate-500 uppercase tracking-wider mb-1">核心技术领域</div>
                    <div class="text-2xl font-bold text-purple-600 truncate" title="{{ dominant_tech }}">{{ dominant_tech }}</div>
                    <div class="mt-2 text-sm text-slate-500">提及频次最高</div>
                </div>

                <div class="glass-card p-6 border-t-4 border-teal-500">
                    <div class="text-sm font-medium text-slate-500 uppercase tracking-wider mb-1">数字技术总频次</div>
                    <div class="text-4xl font-bold text-slate-800">{{ total_tech_count }}</div>
                    <div class="mt-2 text-sm text-slate-500">{{ latest_year }}年</div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                <!-- Main Trend Chart -->
                <div class="lg:col-span-2 glass-card p-6">
                    <h3 class="text-lg font-bold text-slate-700 mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
                        数字化转型指数趋势 (2000-2023)
                    </h3>
                    <div id="trendChart" style="height: 400px; width: 100%;"></div>
                </div>

                <!-- Composition Chart -->
                <div class="glass-card p-6">
                    <h3 class="text-lg font-bold text-slate-700 mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"></path></svg>
                        技术关注度构成 ({{ latest_year }})
                    </h3>
                    <div id="radarChart" style="height: 400px; width: 100%;"></div>
                </div>
            </div>
            
            <!-- Comparison Chart (Keywords Trend) -->
             <div class="glass-card p-6 mb-8">
                <h3 class="text-lg font-bold text-slate-700 mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                    细分技术词频演变
                </h3>
                <div id="keywordChart" style="height: 350px; width: 100%;"></div>
            </div>

            <!-- Data Table -->
            <div class="glass-card overflow-hidden">
                <div class="px-6 py-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
                    <h3 class="font-bold text-slate-700">详细数据列表</h3>
                    <button onclick="document.getElementById('dataTable').classList.toggle('hidden')" class="text-sm text-blue-600 hover:underline">展开/收起</button>
                </div>
                <div id="dataTable" class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-slate-200">
                        <thead class="bg-slate-50">
                            <tr>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">年份</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">转型指数</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">人工智能</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">大数据</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">云计算</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">区块链</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-slate-200">
                            {% for row in data_list %}
                            <tr class="hover:bg-slate-50 transition-colors">
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{{ row['year'] }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-blue-600 font-bold">{{ row['index'] }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{{ row['ai'] }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{{ row['bigdata'] }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{{ row['cloud'] }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{{ row['blockchain'] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            // Data from Flask
            const chartData = {{ chart_data | safe }};
            
            // 1. Trend Chart (Line)
            const trendChart = echarts.init(document.getElementById('trendChart'));
            const trendOption = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'cross' }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: chartData.years
                },
                yAxis: {
                    type: 'value',
                    name: '指数 (0-100)',
                    min: 0
                },
                series: [{
                    name: '数字化转型指数',
                    type: 'line',
                    smooth: true,
                    symbol: 'circle',
                    symbolSize: 8,
                    sampling: 'average',
                    itemStyle: {
                        color: '#2563eb'
                    },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(37, 99, 235, 0.5)' },
                            { offset: 1, color: 'rgba(37, 99, 235, 0.05)' }
                        ])
                    },
                    data: chartData.indices
                }]
            };
            trendChart.setOption(trendOption);

            // 2. Keyword Composition (Radar or Pie - using Radar for tech feel)
            // Using data from the latest year available
            const radarChart = echarts.init(document.getElementById('radarChart'));
            const latestKeywords = chartData.latest_breakdown;
            const radarOption = {
                tooltip: { trigger: 'item' },
                radar: {
                    indicator: [
                        { name: '人工智能', max: Math.max(10, latestKeywords.ai * 1.5) },
                        { name: '大数据', max: Math.max(10, latestKeywords.bigdata * 1.5) },
                        { name: '云计算', max: Math.max(10, latestKeywords.cloud * 1.5) },
                        { name: '区块链', max: Math.max(10, latestKeywords.blockchain * 1.5) }
                    ],
                    radius: '65%',
                    shape: 'circle',
                    splitNumber: 4,
                    axisName: {
                        color: '#64748b'
                    },
                    splitLine: {
                        lineStyle: {
                            color: 'rgba(238, 197, 102, 0.2)'
                        }
                    },
                    splitArea: {
                        show: false
                    },
                    axisLine: {
                        lineStyle: {
                            color: 'rgba(238, 197, 102, 0.5)'
                        }
                    }
                },
                series: [{
                    name: '技术词频构成 (' + chartData.years[chartData.years.length - 1] + ')',
                    type: 'radar',
                    data: [{
                        value: [latestKeywords.ai, latestKeywords.bigdata, latestKeywords.cloud, latestKeywords.blockchain],
                        name: '技术关注度',
                        areaStyle: {
                            color: 'rgba(129, 140, 248, 0.6)'
                        },
                        itemStyle: {
                            color: '#6366f1'
                        }
                    }]
                }]
            };
            radarChart.setOption(radarOption);

            // 3. Keyword Evolution Chart (Stacked Bar or Multi-line)
            const keywordChart = echarts.init(document.getElementById('keywordChart'));
            const keywordOption = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' }
                },
                legend: {
                    data: ['人工智能', '大数据', '云计算', '区块链'],
                    bottom: 0
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '10%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: chartData.years
                },
                yAxis: {
                    type: 'value',
                    name: '词频数'
                },
                series: [
                    {
                        name: '人工智能',
                        type: 'bar',
                        stack: 'total',
                        emphasis: { focus: 'series' },
                        data: chartData.breakdown.ai
                    },
                    {
                        name: '大数据',
                        type: 'bar',
                        stack: 'total',
                        emphasis: { focus: 'series' },
                        data: chartData.breakdown.bigdata
                    },
                    {
                        name: '云计算',
                        type: 'bar',
                        stack: 'total',
                        emphasis: { focus: 'series' },
                        data: chartData.breakdown.cloud
                    },
                    {
                        name: '区块链',
                        type: 'bar',
                        stack: 'total',
                        emphasis: { focus: 'series' },
                        data: chartData.breakdown.blockchain
                    }
                ]
            };
            keywordChart.setOption(keywordOption);

            // Resize charts on window resize
            window.addEventListener('resize', function() {
                trendChart.resize();
                radarChart.resize();
                keywordChart.resize();
            });
        </script>
        {% endif %}
    </main>

    <footer class="bg-white border-t border-slate-200 mt-12 py-8">
        <div class="container mx-auto px-4 text-center text-slate-500 text-sm">
            <p>&copy; 2025 上市公司数字化转型洞察系统 | Powered by Flask & ECharts</p>
        </div>
    </footer>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    query = ''
    search_type = 'name'
    error = None
    company_name = None
    stock_code = None
    data_list = []
    chart_data = '{}'
    latest_index = 0
    latest_year = ''
    avg_index = 0
    index_change = 0
    dominant_tech = '无'
    total_tech_count = 0

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        search_type = request.form.get('search_type', 'name')
        
        if query:
            if df.empty:
                error = "数据未加载，请检查CSV文件路径。"
            else:
                matched_df = pd.DataFrame()
                
                if search_type == 'code':
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
                        error = f"找到企业 {company_name} ({stock_code})，但没有2000-2023年的数据。"
                    else:
                        # Prepare lists for chart and table
                        years = []
                        indices = []
                        
                        # Breakdown lists
                        ai_list = []
                        bd_list = []
                        cc_list = []
                        bc_list = []

                        for _, row in company_df.iterrows():
                            year = int(row['年份'])
                            val = row['数字化转型指数(0-100分)']
                            
                            ai_val = int(row.get('人工智能词频数', 0))
                            bd_val = int(row.get('大数据词频数', 0))
                            cc_val = int(row.get('云计算词频数', 0))
                            bc_val = int(row.get('区块链词频数', 0))
                            
                            data_list.append({
                                'year': year,
                                'index': val,
                                'ai': ai_val,
                                'bigdata': bd_val,
                                'cloud': cc_val,
                                'blockchain': bc_val
                            })
                            
                            years.append(year)
                            indices.append(val)
                            ai_list.append(ai_val)
                            bd_list.append(bd_val)
                            cc_list.append(cc_val)
                            bc_list.append(bc_val)
                        
                        # Calculate statistics
                        if indices:
                            latest_index = indices[-1]
                            latest_year = years[-1]
                            avg_index = round(sum(indices) / len(indices), 2)
                            
                            # YoY Change
                            if len(indices) >= 2:
                                index_change = round(indices[-1] - indices[-2], 2)
                            else:
                                index_change = 0
                            
                            # Dominant Tech in latest year
                            latest_counts = {
                                '人工智能': ai_list[-1],
                                '大数据': bd_list[-1],
                                '云计算': cc_list[-1],
                                '区块链': bc_list[-1]
                            }
                            # Find max key
                            max_tech = max(latest_counts, key=latest_counts.get)
                            if latest_counts[max_tech] > 0:
                                dominant_tech = max_tech
                            else:
                                dominant_tech = "暂无显著偏好"

                            total_tech_count = sum(latest_counts.values())

                        chart_data = json.dumps({
                            'years': years,
                            'indices': indices,
                            'breakdown': {
                                'ai': ai_list,
                                'bigdata': bd_list,
                                'cloud': cc_list,
                                'blockchain': bc_list
                            },
                            'latest_breakdown': {
                                'ai': ai_list[-1] if ai_list else 0,
                                'bigdata': bd_list[-1] if bd_list else 0,
                                'cloud': cc_list[-1] if cc_list else 0,
                                'blockchain': bc_list[-1] if bc_list else 0
                            }
                        })
                else:
                    error = "未找到该企业或股票代码的数据。"

    return render_template_string(HTML_TEMPLATE, 
                                  query=query, 
                                  search_type=search_type,
                                  error=error, 
                                  company_name=company_name, 
                                  stock_code=stock_code,
                                  data_list=reversed(data_list),
                                  chart_data=chart_data,
                                  latest_index=latest_index,
                                  latest_year=latest_year,
                                  avg_index=avg_index,
                                  index_change=index_change,
                                  dominant_tech=dominant_tech,
                                  total_tech_count=total_tech_count)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
