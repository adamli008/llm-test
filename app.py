import streamlit as st
import requests
import time
import json
import os
import base64

# ================= 基础配置 =================
st.set_page_config(page_title="AI 模型测试台", layout="wide")

# 初始化对话上下文缓存
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

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
        
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            model_name = st.text_input("Model Name (模型名称)", value="agnes-2.0-flash")
        with col_m2:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("🗑️ 清空记忆", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

        prompt = st.text_area("User Content (发送新消息)", value="你好")
        
        # 将历史记录与新输入合并，生成给 API 调用的上下文
        current_msgs = st.session_state.chat_messages.copy()
        if prompt.strip():
            current_msgs.append({"role": "user", "content": prompt.strip()})
            
        payload = {
            "model": model_name,
            "messages": current_msgs
        }
        
    elif model_type == "图片模型":
        api_url = "https://apihub.agnes-ai.com/v1/images/generations"
        model_name = st.text_input("Model Name (模型名称)", value="agnes-image-2.1-flash")
        
        # 新增：图生图/文生图 模式切换
        generation_mode = st.radio("生成模式 (Generation Mode)", ["文生图 (Text-to-Image)", "图生图 (Image-to-Image)"], horizontal=True)
        
        prompt = st.text_area("Prompt (提示词)", value="一只可爱的猫咪")
        
        import base64
        
        image_url_input = ""
        base64_image = ""
        
        if generation_mode == "图生图 (Image-to-Image)":
            st.write("**传入参考图片** (本地上传或输入URL均可，优先使用本地)")
            col_img_up1, col_img_up2 = st.columns(2)
            with col_img_up1:
                uploaded_image = st.file_uploader("📂 本地图片上传", type=["png", "jpg", "jpeg"])
                if uploaded_image is not None:
                    bytes_data = uploaded_image.getvalue()
                    ext = uploaded_image.name.split('.')[-1].lower()
                    mime = "image/png" if ext == "png" else "image/jpeg"
                    base64_image = f"data:{mime};base64,{base64.b64encode(bytes_data).decode('utf-8')}"
                    st.success("✅ 本地图片已读取 (Base64)")
            with col_img_up2:
                image_url_input = st.text_input("🔗 或输入参考图片 URL", placeholder="https://example.com/image.jpg")
            
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
            "model": model_name, 
            "prompt": prompt, 
            "size": size
        }
        
        if generation_mode == "图生图 (Image-to-Image)":
            img_param = base64_image if base64_image else image_url_input.strip()
            if img_param:
                # 完全对齐官方 API Doc：使用 extra_body，并将图片(Base64或URL)放入列表
                payload["extra_body"] = {
                    "image": [
                        img_param
                    ],
                    "response_format": "url"
                }
            
    elif model_type == "视频模型":
        api_url = "https://apihub.agnes-ai.com/v1/videos"
        model_name = st.text_input("Model Name (模型名称)", value="agnes-video-v2.0")
        
        # 新增：图生视频/文生视频/多图生视频/首尾帧生视频 模式切换
        video_generation_mode = st.radio("视频生成模式 (Generation Mode)", ["文生视频 (Text-to-Video)", "图生视频 (Image-to-Video)", "多图生视频 (Multi-Image-to-Video)", "首尾帧生视频 (Keyframes-to-Video)"], horizontal=True)
        
        # 根据不同模式提供不同的默认 Prompt
        default_prompt = "The woman slowly turns around and looks back at the camera, natural facial expression, cinematic camera movement"
        if video_generation_mode == "多图生视频 (Multi-Image-to-Video)":
            default_prompt = "Create a smooth transformation scene between the two reference images, cinematic lighting, consistent character identity, natural motion"
        elif video_generation_mode == "首尾帧生视频 (Keyframes-to-Video)":
            default_prompt = "Generate a smooth cinematic transition between the keyframes, maintaining visual consistency and natural camera movement"
            
        prompt = st.text_area("Prompt (提示词)", value=default_prompt)
        
        video_image_url_input = ""
        multi_video_urls = ""
        keyframes_urls = ""
        if video_generation_mode == "图生视频 (Image-to-Video)":
            video_image_url_input = st.text_input("起始图片 URL (Source Image URL)", placeholder="https://example.com/image.png")
            st.caption("提示：请提供可公开访问的图片 URL 链接")
        elif video_generation_mode == "多图生视频 (Multi-Image-to-Video)":
            multi_video_urls = st.text_area("多张参考图片 URL (一行一个)", placeholder="https://example.com/image1.png\nhttps://example.com/image2.png")
            st.caption("提示：每行填写一个可公开访问的图片 URL 链接")
        elif video_generation_mode == "首尾帧生视频 (Keyframes-to-Video)":
            keyframes_urls = st.text_area("首尾关键帧图片 URL (首帧和尾帧各一行)", placeholder="https://example.com/keyframe1.png\nhttps://example.com/keyframe2.png")
            st.caption("提示：请务必提供2张可公开访问的图片 URL 链接（第一行为起幅，第二行为止幅）")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            width = st.number_input("宽度 (Width)", value=1152)
            height = st.number_input("高度 (Height)", value=768)
        with col_v2:
            num_frames = st.number_input("总帧数 (Num Frames)", value=121)
            frame_rate = st.number_input("帧率 (Frame Rate)", value=24)
            
        payload = {
            "model": model_name, "prompt": prompt,
            "width": int(width), "height": int(height),
            "num_frames": int(num_frames), "frame_rate": int(frame_rate)
        }
        
        if video_generation_mode == "图生视频 (Image-to-Video)" and video_image_url_input.strip():
            payload["image"] = video_image_url_input.strip()
        elif video_generation_mode == "多图生视频 (Multi-Image-to-Video)" and multi_video_urls.strip():
            # 按行分割提取多个 URL
            url_list = [url.strip() for url in multi_video_urls.strip().split('\n') if url.strip()]
            if url_list:
                payload["extra_body"] = {
                    "image": url_list
                }
        elif video_generation_mode == "首尾帧生视频 (Keyframes-to-Video)" and keyframes_urls.strip():
            url_list = [url.strip() for url in keyframes_urls.strip().split('\n') if url.strip()]
            if url_list:
                payload["extra_body"] = {
                    "image": url_list,
                    "mode": "keyframes"
                }
            
    submit_button = st.button("发送并等待结果", type="primary", use_container_width=True)
    
    # --- 在按钮下方展示实时生成的 cURL 命令 ---
    st.markdown("---")
    st.markdown("#### 🔍 对应的 cURL 命令")
    
    # 针对 cURL 显示，如果包含超长的 base64，可以做个截断，避免卡死前端
    display_payload = payload.copy()
    if display_payload.get("image_url", "").startswith("data:image"):
        img_url = display_payload["image_url"]
        if len(img_url) > 100:
            display_payload["image_url"] = img_url[:50] + "...[Base64 字符串太长已截断展示]..."
            
    payload_str = json.dumps(display_payload, ensure_ascii=False).replace('"', '\\"')
    
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
    
    try:
        # ----------------- 1. 对话模型逻辑 -----------------
        if model_type == "对话模型":
            
            # 发送消息并合并上下文
            if submit_button and prompt.strip():
                st.session_state.chat_messages.append({"role": "user", "content": prompt.strip()})
                payload["messages"] = st.session_state.chat_messages
                
                with st.spinner('正在请求对话模型...'):
                    res = requests.post(api_url, json=payload, headers=HEADERS_POST).json()
                    
                    if "choices" in res:
                        reply = res["choices"][0]["message"]["content"]
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                        st.success("请求成功！")
                    else:
                        st.error("请求发生异常，未获取到回复内容。")
                        if len(st.session_state.chat_messages) > 0:
                            st.session_state.chat_messages.pop() # 移除失败的最后一条消息
                    
                    with st.expander("查看原始 JSON 返回", expanded=False):
                        st.json(res)
            
            # 渲染记忆面板：使用原生的 chat_message 组件
            st.markdown("### 💬 会话上下文")
            if len(st.session_state.chat_messages) == 0:
                st.info("👆 记忆为空。请在左侧发送新消息以开启多轮对话。")
            else:
                chat_container = st.container(height=600)
                with chat_container:
                    for msg in st.session_state.chat_messages:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["content"])

        # ----------------- 2. 图片模型逻辑 -----------------
        elif model_type == "图片模型":
            if submit_button:
                start_time = time.time()
                with st.spinner('正在生成图片...'):
                    res = requests.post(api_url, json=payload, headers=HEADERS_POST).json()
                    end_time = time.time()
                    cost_time = end_time - start_time
                    
                    # 记录 Debug 日志到本地文件
                    with open("debug_response.json", "w", encoding="utf-8") as f:
                        json.dump(res, f, ensure_ascii=False, indent=2)
                        
                    if "data" in res and len(res["data"]) > 0:
                        image_data = res["data"][0]
                        
                        # 仅展示生成耗时
                        st.caption(f"⏱️ **耗时:** `{cost_time:.2f}` 秒")
                        
                        if "b64_json" in image_data and image_data["b64_json"]:
                            # 渲染 Base64 图像
                            b64_str = image_data["b64_json"]
                            st.image(f"data:image/png;base64,{b64_str}", caption="生成的图片 (Base64)", use_container_width=True)
                            st.success("图片已成功生成并使用 Base64 数据渲染！")
                        elif "url" in image_data and image_data["url"]:
                            image_url = str(image_data["url"]).strip()
                            
                            # 防御性解析 1：如果 API 错误地把 base64 塞进了 url 字段
                            if image_url.startswith("data:image"):
                                st.image(image_url, caption="生成的图片 (Base64 from URL field)", use_container_width=True)
                                st.success("已通过 Data URI 渲染图片！")
                            else:
                                # 防御性解析 2：如果 API 返回了 Markdown 格式的图片 `![alt](url)`
                                if image_url.startswith("![") and "](" in image_url:
                                    import re
                                    match = re.search(r'\]\((.*?)\)', image_url)
                                    if match:
                                        image_url = match.group(1)
                                
                                # 常规 URL 处理
                                if not image_url.startswith("http") and not image_url.startswith("//"):
                                    image_url = "https://" + image_url
                                elif image_url.startswith("//"):
                                    image_url = "https:" + image_url
                                
                                st.image(image_url, caption="生成的图片 (URL)", use_container_width=True)
                                st.success(f"图片链接: {image_url}")
                        else:
                            st.error(f"解析失败：返回的 data 中既没有 url 也没有 b64_json 字段。实际内容为: {image_data}")
                    else:
                        st.error("生成异常，未获取到图片数据")
                        
                    with st.expander("查看原始 JSON 返回", expanded=False):
                        # 如果是 b64_json，展示 JSON 时截断超长的 base64，防止页面卡死
                        display_res = res.copy()
                        if "data" in display_res and len(display_res["data"]) > 0 and display_res["data"][0].get("b64_json"):
                            display_res["data"][0]["b64_json"] = display_res["data"][0]["b64_json"][:50] + "...[Base64 数据过长已截断展示]..."
                        st.json(display_res)

        # ----------------- 3. 视频模型逻辑 -----------------
        elif model_type == "视频模型":
            if submit_button:
                start_time = time.time()
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
                        status.update(label=f"任务已提交，Task ID: {task_id}。正在无限轮询排队生成中...", state="running")
                        
                        url_query = f"https://apihub.agnes-ai.com/v1/videos/{task_id}"
                        
                        i = 0
                        while True:
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
                                i += 1
                                status.update(label=f"⏳ 任务排队/处理中... (已查询 {i} 次，每 10 秒刷新)")
                                time.sleep(10)
                
                # 跳出 status 框后，在页面主体直接渲染视频
                if task_success:
                    end_time = time.time()
                    cost_time = end_time - start_time
                    
                    # 仅展示生成耗时
                    st.caption(f"⏱️ **耗时:** `{cost_time:.2f}` 秒")
                        
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