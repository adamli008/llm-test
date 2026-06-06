import streamlit as st
import requests
import time
import json
import os

# ================= 基础配置 =================
st.set_page_config(page_title="AI 模型测试台", layout="wide")

# 从环境变量获取，或者在侧边栏让用户输入
API_KEY = os.environ.get("AGNES_API_KEY", "")

# 如果环境变量没有配置，就在网页侧边栏加一个密码输入框
if not API_KEY:
    with st.sidebar:
        st.warning("请先配置 API Key")
        API_KEY = st.text_input("请输入您的 Agnes API Key:", type="password")

if not API_KEY:
    st.info("👈 请在左侧输入 API Key 后开始使用")
    st.stop() # 停止运行下面的代码，直到输入了 Key

HEADERS_POST = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
HEADERS_GET = {
    "Authorization": f"Bearer {API_KEY}"
}

# ================= 界面布局 =================
col1, col2 = st.columns([1, 1]) # 左右等宽两列

with col1:
    st.header("⚙️ 配置模型参数")
    model_type = st.selectbox("Model Type (模型类型)", ["对话模型", "图片模型", "视频模型"])
    
    # --- 动态渲染表单，并同时构建 Payload 与 URL ---
    payload = {}
    api_url = ""
    
    if model_type == "对话模型":
        api_url = "https://apihub.agnes-ai.com/v1/chat/completions"
        model_name = st.text_input("Model Name (模型名称)", value="agnes-2.0-flash")
        prompt = st.text_area("User Content (用户输入)", value="你好")
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        
    elif model_type == "图片模型":
        api_url = "https://apihub.agnes-ai.com/v1/images/generations"
        model_name = st.text_input("Model Name (模型名称)", value="agnes-image-2.1-flash")
        prompt = st.text_area("Prompt (提示词)", value="一只可爱的猫咪")
        
        # 定义比例与其对应的5个典型尺寸映射
        ratio_to_sizes = {
            "1:1 (方形)": {
                "512x512 (基础)": "512x512",
                "768x768 (进阶)": "768x768",
                "1024x1024 (高清/推荐)": "1024x1024",
                "1536x1536 (超清)": "1536x1536",
                "2048x2048 (极清)": "2048x2048"
            },
            "16:9 (横屏)": {
                "912x512 (基础)": "912x512",
                "1024x576 (进阶)": "1024x576",
                "1280x720 (720p 高清/推荐)": "1280x720",
                "1920x1080 (1080p 超清)": "1920x1080",
                "2560x1440 (2K 极清)": "2560x1440"
            },
            "9:16 (竖屏)": {
                "512x912 (基础)": "512x912",
                "576x1024 (进阶)": "576x1024",
                "720x1280 (720p 高清/推荐)": "720x1280",
                "1080x1920 (1080p 超清)": "1080x1920",
                "1440x2560 (2K 极清)": "1440x2560"
            }
        }
        
        # 将下拉框并排显示
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            selected_ratio = st.selectbox("图片比例 (Aspect Ratio)", list(ratio_to_sizes.keys()))
        
        with col_img2:
            available_sizes = ratio_to_sizes[selected_ratio]
            selected_size_label = st.selectbox("图片大小 (Resolution)", list(available_sizes.keys()), index=2)
        
        size = available_sizes[selected_size_label] 
        
        payload = {
            "model": model_name, "prompt": prompt, "size": size
        }
        
    elif model_type == "视频模型":
        api_url = "https://apihub.agnes-ai.com/v1/videos"
        model_name = st.text_input("Model Name (模型名称)", value="agnes-video-v2.0")
        prompt = st.text_area("Prompt (提示词)", value="比基尼美女在海边跑步")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            width = st.number_input("宽度 (Width)", value=1152)
            height = st.number_input("高度 (Height)", value=768)
        with col_v2:
            num_frames = st.number_input("总帧数 (Num Frames)", value=241)
            frame_rate = st.number_input("帧率 (Frame Rate)", value=24)
            
        payload = {
            "model": model_name, "prompt": prompt,
            "width": int(width), "height": int(height),
            "num_frames": int(num_frames), "frame_rate": int(frame_rate)
        }
            
    submit_button = st.button("发送并等待结果", type="primary", use_container_width=True)
    
    # --- 在按钮下方展示实时生成的 cURL 命令 ---
    st.markdown("---")
    st.markdown("#### 🔍 对应的 cURL 命令")
    
    payload_str = json.dumps(payload, ensure_ascii=False).replace('"', '\\"')
    
    curl_post = f"""curl -X POST "{api_url}" \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer {API_KEY}" \\
-d "{payload_str}" """
    
    st.code(curl_post, language="bash")
    
    if model_type == "视频模型":
        st.markdown("**查询视频结果的 cURL (将 task_id 替换为实际返回的 ID):**")
        curl_get = f"""curl "https://apihub.agnes-ai.com/v1/videos/task_id" \\
-H "Authorization: Bearer {API_KEY}" """
        st.code(curl_get, language="bash")

# ================= 处理结果区域 =================
with col2:
    st.header("💻 处理结果")
    
    if submit_button:
        try:
            # ----------------- 1. 对话模型逻辑 -----------------
            if model_type == "对话模型":
                with st.spinner('正在请求对话模型...'):
                    res = requests.post(api_url, json=payload, headers=HEADERS_POST).json()
                    
                    if "choices" in res:
                        reply = res["choices"][0]["message"]["content"]
                        st.success("请求成功！")
                        st.info(reply)
                    else:
                        st.error("请求发生异常，未获取到回复内容。")
                    
                    with st.expander("查看原始 JSON 返回", expanded=False):
                        st.json(res)

            # ----------------- 2. 图片模型逻辑 -----------------
            elif model_type == "图片模型":
                with st.spinner('正在生成图片...'):
                    res = requests.post(api_url, json=payload, headers=HEADERS_POST).json()
                    
                    if "data" in res and len(res["data"]) > 0:
                        image_url = res["data"][0]["url"]
                        
                        # 如果 API 返回的 URL 没有 http 前缀，手动加上 https://
                        if not image_url.startswith("http"):
                            image_url = "https://" + image_url
                            
                        st.image(image_url, caption="生成的图片", use_container_width=True)
                        st.success(f"图片链接: {image_url}")
                    else:
                        st.error("生成异常，未获取到图片 URL")
                        
                    with st.expander("查看原始 JSON 返回", expanded=False):
                        st.json(res)

            # ----------------- 3. 视频模型逻辑 -----------------
            elif model_type == "视频模型":
                final_video_url = None
                final_json = None
                task_success = False
                
                with st.status("🎬 正在提交视频任务...") as status:
                    res_create = requests.post(api_url, json=payload, headers=HEADERS_POST).json()
                    task_id = res_create.get("id") or res_create.get("task_id")
                    
                    if not task_id:
                        status.update(label="提交失败，未获取到 task_id", state="error")
                        final_json = res_create
                    else:
                        status.update(label=f"任务已提交，Task ID: {task_id}。正在排队生成中...", state="running")
                        
                        url_query = f"https://apihub.agnes-ai.com/v1/videos/{task_id}"
                        max_retries = 60 # 最多等 10 分钟
                        
                        for i in range(max_retries):
                            res_query = requests.get(url_query, headers=HEADERS_GET).json()
                            video_state = res_query.get("state") or res_query.get("status")
                            
                            if video_state in ["success", "succeeded", "completed"]:
                                status.update(label="视频生成完成！", state="complete")
                                final_video_url = res_query.get("remixed_from_video_id")
                                
                                if final_video_url and not final_video_url.startswith("http"):
                                    final_video_url = "https://" + final_video_url
                                    
                                final_json = res_query
                                task_success = True
                                break
                            
                            elif video_state in ["failed", "error"]:
                                status.update(label="视频生成失败！", state="error")
                                final_json = res_query
                                break
                                
                            else:
                                status.update(label=f"任务排队/处理中 (第 {i+1} 次查询，Task ID: {task_id})...")
                                time.sleep(10)
                        else:
                            status.update(label="已达到最大等待时间，请稍后手动通过 Task ID 查询", state="error")
                
                # 跳出 status 框后，在页面主体直接渲染视频
                if task_success:
                    if final_video_url:
                        st.video(final_video_url)
                        st.success(f"视频链接: {final_video_url}")
                    else:
                        st.warning("状态显示成功，但未能在 'remixed_from_video_id' 字段找到视频链接。")
                
                # 将 JSON 放在折叠面板中
                if final_json is not None:
                    with st.expander("查看原始 JSON 返回", expanded=False):
                        st.json(final_json)
                            
        except Exception as e:
            st.error(f"发生网络请求错误或代码异常: {e}")
