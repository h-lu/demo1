import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx
import pandas as pd

# 加载环境变量
load_dotenv()

# 初始化主题设置
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# 定义粉色主题的颜色
colors = {
    'light': {
        'bg': '#fff0f5',  # 浅粉色背景
        'secondary_bg': '#ffe4e1',  # 蜜桃色
        'text': '#ff69b4',  # 粉红色文字
        'primary': '#ff1493',  # 深粉红
        'primary_hover': '#ff69b4',  # 亮粉红
        'secondary_text': '#ff69b4'  # 粉红色次要文字
    },
    'dark': {
        'bg': '#2d2d2d',
        'secondary_bg': '#363636',
        'text': '#fff0f5',
        'primary': '#ff69b4',
        'primary_hover': '#ff1493',
        'secondary_text': '#ffb6c1'
    }
}

# 获取当前主题的颜色
theme_colors = colors[st.session_state.theme]

# 初始化历史记录
if 'history' not in st.session_state:
    st.session_state.history = []

# 获取 API 密钥
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    # 如果环境变量中没有找到，尝试从 .env 文件加载
    try:
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
    except:
        pass
    
    # 如果还是没有 API 密钥，使用 Streamlit 的密钥输入
    if not api_key:
        api_key = st.sidebar.text_input("请输入 DeepSeek API 密钥", type="password")
        if not api_key:
            st.error("请提供 DeepSeek API 密钥才能继续使用")
            st.stop()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    http_client=httpx.Client(
        timeout=httpx.Timeout(60.0)
    )
)

# 添加 get_ai_response 函数定义
def get_ai_response(prompt, response_type, stream=True):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stream=stream
        )
        
        # 记录对话历史
        history_item = {
            'type': response_type,
            'prompt': prompt,
            'response': '',
            'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if stream:
            return response, history_item
        else:
            full_response = ''.join([chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content])
            history_item['response'] = full_response
            st.session_state.history.append(history_item)
            return full_response
            
    except Exception as e:
        st.error(f"获取AI响应时出错：{str(e)}")
        return None

# 设置页面配置
st.set_page_config(
    page_title="Hello Kitty 生活助手",
    page_icon="🎀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加自定义CSS样式
st.markdown("""
    <style>
        /* 整体背景和基础样式 */
        .stApp {
            background: linear-gradient(135deg, #fff5f9 0%, #fff0f5 100%);
            background-image: 
                radial-gradient(circle at center, rgba(255, 255, 255, 0.8) 2px, transparent 2px),
                linear-gradient(135deg, #fff5f9 0%, #fff0f5 100%);
            background-size: 25px 25px, 100% 100%;
        }
        
        /* 卡片样式 */
        .info-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            border: 1px solid #ffd1dc;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(255, 182, 193, 0.1);
            transition: all 0.3s ease;
        }
        
        .info-card:hover {
            box-shadow: 0 6px 20px rgba(255, 182, 193, 0.15);
            transform: translateY(-2px);
        }
        
        /* 按钮样式 */
        .stButton>button {
            background: linear-gradient(45deg, #ffb6c1, #ffc0cb);
            border: none;
            border-radius: 25px;
            color: white;
            font-weight: 500;
            padding: 0.5rem 2rem;
            box-shadow: 0 3px 10px rgba(255, 182, 193, 0.2);
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background: linear-gradient(45deg, #ffc0cb, #ffb6c1);
            box-shadow: 0 5px 15px rgba(255, 182, 193, 0.3);
            transform: translateY(-2px);
        }
        
        /* 输入框样式 */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            border-radius: 15px;
            border: 1px solid #ffd1dc;
            background-color: white;
            padding: 1rem;
        }
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #ffb6c1;
            box-shadow: 0 0 0 2px rgba(255, 182, 193, 0.2);
        }
        
        /* 选择器样式 */
        .stSelectbox>div>div {
            background: white;
            border-radius: 15px;
            border: 1px solid #ffd1dc;
        }
        
        /* 单选按钮组样式 */
        .stRadio>div {
            background: white;
            padding: 1rem;
            border-radius: 15px;
            border: 1px solid #ffd1dc;
        }
        
        /* 标题样式 */
        h1, h2, h3 {
            color: #ff8da1;
            font-weight: 600;
        }
        
        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: white;
            border-radius: 15px;
            padding: 0.5rem 1rem;
            color: #ff8da1;
            border: 1px solid #ffd1dc;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #ff8da1;
            color: white;
            border: none;
        }
        
        /* 分割线样式 */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #ffd1dc, transparent);
            margin: 2rem 0;
        }
        
        /* 历史记录样式 */
        .history-item {
            background: white;
            border-radius: 15px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid #ffd1dc;
            box-shadow: 0 2px 8px rgba(255, 182, 193, 0.1);
        }
        
        /* 滚动条美化 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #fff5f9;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #ffb6c1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #ff8da1;
        }
    </style>
""", unsafe_allow_html=True)

# 在页面标题之后添加顶部工具栏
st.markdown("""
    <style>
        .top-toolbar {
            background-color: rgba(255,240,245,0.9);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 2px solid #ff69b4;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .toolbar-section {
            flex: 1;
            margin: 0 10px;
        }
        
        .mood-buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        
        .mood-button {
            padding: 5px 15px;
            border-radius: 20px;
            border: 2px solid #ff69b4;
            background-color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .mood-button:hover, .mood-button.active {
            background-color: #ff69b4;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# 页面标题
st.title("🎀 Hello Kitty 生活小助手")

# 顶部工具栏
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("### ✨ 选择场景")
    life_scenario = st.selectbox(
        "",
        ["美食探店", "穿搭搭配", "护肤美妆", "居家收纳", 
         "健康养生", "心情治愈", "学习提升", "兴趣手作",
         "职场技能", "恋爱相处", "宠物护理", "旅行攻略"],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 💝 今日心情")
    mood = st.radio(
        "",
        ["开心", "平静", "疲惫", "焦虑", "需要治愈"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col3:
    st.markdown("### 🌟 选择星座")
    zodiac = st.selectbox(
        "",
        ["白羊座", "金牛座", "双子座", "巨蟹座", 
         "狮子座", "处女座", "天秤座", "天蝎座",
         "射手座", "摩羯座", "水瓶座", "双鱼座"],
        label_visibility="collapsed"
    )

# 添加分隔线
st.markdown("---")

# 主界面标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💫 灵感推荐", "💡 生活妙招", "💝 心情小屋", "🌟 今日运势", "📜 历史记录"])

# 灵感推荐标签页
with tab1:
    st.markdown(f"""
        <div class="info-card">
            <h3 style='color: {theme_colors['primary']}; margin: 0;'>✨ 今日生活灵感</h3>
            <p style='margin: 0.5rem 0 0 0;'>为您推荐适合的生活创意和小技巧</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✨ 获取灵感", key="inspiration"):
        prompt = f"""作为一个生活博主，请根据以下场景提供新颖实用的建议：
        - 场景：{life_scenario}
        - 心情：{mood}

        请提供：
        1. 3-5个实用小技巧
        2. 适合的参考案例
        3. 注意事项
        4. 新手友好的建议
        5. 博主私藏tips
        
        请用清新活泼的语气，以markdown格式输出。"""
        
        with st.spinner("正在寻找灵感..."):
            response_placeholder = st.empty()
            full_response = ""
            
            response_stream, history_item = get_ai_response(prompt, "灵感推荐")
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response)
            
            history_item['response'] = full_response
            st.session_state.history.append(history_item)

# 生活妙招标签页
with tab2:
    st.markdown(f"""
        <div class="info-card">
            <h3 style='color: {theme_colors['primary']}; margin: 0;'>💫 实用生活妙招</h3>
            <p style='margin: 0.5rem 0 0 0;'>解决生活中的各种小困扰</p>
        </div>
    """, unsafe_allow_html=True)
    
    specific_issue = st.text_input(
        "💭 遇到什么困扰呢？", 
        placeholder="例如：如何快速整理衣柜、护肤品使用顺序、美食拍照技巧等"
    )
    
    if st.button("💫 获取妙招", key="tips"):
        if not specific_issue:
            st.warning("请先告诉我您的困扰~")
        else:
            prompt = f"""请为以下问题提供实用的解决方案：
            - 问题：{specific_issue}
            - 场景：{life_scenario}

            请提供：
            1. 问题分析
            2. 3-5个解决妙招
            3. 实操步骤
            4. 避坑指南
            5. 进阶建议
            
            请用活泼可爱的语气，以markdown格式输出。"""
            
            with st.spinner("正在整理妙招..."):
                response_placeholder = st.empty()
                full_response = ""
                
                response_stream, history_item = get_ai_response(prompt, "生活妙招")
                for chunk in response_stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response)
                
                history_item['response'] = full_response
                st.session_state.history.append(history_item)

# 心情小屋标签页
with tab3:
    st.markdown(f"""
        <div class="info-card">
            <h3 style='color: {theme_colors['primary']}; margin: 0;'>💝 今日心情小屋</h3>
            <p style='margin: 0.5rem 0 0 0;'>分享心情，获取温暖治愈的建议</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("💝 获取治愈", key="healing"):
        prompt = f"""请根据当前心情提供温暖治愈的建议：
        - 心情：{mood}
        - 场景：{life_scenario}
        
        请提供：
        1. 温暖的开场白
        2. 3-5个治愈建议
        3. 适合的音乐推荐
        4. 美食安利
        5. 治愈的生活仪式感
        
        请用温暖治愈的语气，以markdown格式输出。"""
        
        with st.spinner("正在准备治愈良方..."):
            response_placeholder = st.empty()
            full_response = ""
            
            response_stream, history_item = get_ai_response(prompt, "心情小屋")
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response)
            
            history_item['response'] = full_response
            st.session_state.history.append(history_item)

# 添加今日运势标签页
with tab4:
    st.markdown(f"""
        <div class="info-card">
            <h3 style='color: #ff8da1; margin: 0;'>🌟 今日运势解析</h3>
            <p style='margin: 0.5rem 0 0 0;'>为您解读今日星座运势</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🌟 查看运势", key="fortune"):
        prompt = f"""请为{zodiac}提供今日运势解读：
        - 星座：{zodiac}
        - 当前心情：{mood}
        
        请提供以下内容：
        1. 今日运势总评（1-5颗星）
        2. 幸运指数
           - 爱情运：★★★★☆
           - 事业运：★★★★★
           - 财运：★★★☆☆
           - 健康运：★★★★☆
        3. 幸运色和幸运数字
        4. 今日宜忌
        5. 运势详解
           - 感情方面
           - 工作方面
           - 财运方面
           - 健康建议
        6. 开运小贴士
        
        请用温暖活泼的语气，以markdown格式输出，可以适当加入emoji装饰。"""
        
        with st.spinner(f"正在为{zodiac}解读今日运势..."):
            response_placeholder = st.empty()
            full_response = ""
            
            response_stream, history_item = get_ai_response(prompt, "今日运势")
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response)
            
            history_item['response'] = full_response
            st.session_state.history.append(history_item)

# 历史记录标签页
with tab5:
    # 添加标题行，包含清空按钮
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"""
            <div class="info-card">
                <h3 style='color: #ff8da1; margin: 0;'>📜 对话历史记录</h3>
                <p style='margin: 0.5rem 0 0 0;'>查看您的历史对话记录。</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🗑️ 清空记录", key="clear_history"):
            st.session_state.history = []
            st.experimental_rerun()
    
    if not st.session_state.history:
        st.info("暂无历史记录")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"💬 {item['type']} - {item['timestamp']}", expanded=(i == 0)):
                st.markdown("**您的需求：**")
                st.markdown(item['prompt'])
                st.markdown("**AI 回复：**")
                st.markdown(item['response'])
                st.markdown("---")

# 页面底部信息
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #ff69b4;'>
        <p>💝 每一天都是独特的，让我们一起创造美好生活 💝</p>
        <p style='font-size: 0.8em;'>由 AI 提供支持 | 仅供参考</p>
    </div>
""", unsafe_allow_html=True) 