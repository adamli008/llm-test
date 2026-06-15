# 🚀 AI 模型综合测试台 (AI Model Tester)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

这是一个基于 **Streamlit** 构建的轻量级、现代化的 Web 应用程序，专门用于快速测试大语言模型（LLM）、图像生成模型（文生图/图生图）以及丰富的视频生成模型。

它将原本繁琐的终端 `cURL` 请求转化为直观的图形用户界面 (GUI)，让 AI 接口的调试和效果验证变得前所未有地简单。

---

## ✨ 核心功能亮点

### 1. 💬 对话模型 (Chat Completions)
*   **支持模型**: 默认配置 `agnes-2.0-flash`。
*   **特性**: 快速验证文本生成与对话能力，响应结果清晰渲染，支持长文本阅读。

### 2. 🎨 图片模型 (Image Generations)
*   **双模切换**: 完美支持 **文生图 (Text-to-Image)** 和 **图生图 (Image-to-Image)**。
    *   *图生图模式下不仅支持直接输入参考图片公网 URL，还新增支持了**本地图片直传**（自动转 Base64，优先使用本地文件）。*
*   **人性化尺寸选择**: 提供直观的比例选择（1:1 方形、16:9 横屏、9:16 竖屏），并自动映射推荐的 5 种典型分辨率（从基础到极清）。
*   **超强防御性渲染**: 
    *   自动处理 API 返回的 Base64 格式并渲染。
    *   自动检测并修复缺失 `https://` 协议头的图片链接。
    *   自动从 Markdown 格式的返回值（如 `![alt](url)`）中提取真实 URL。

### 3. 🎬 视频模型 (Video Generations)
*   **四大生成模式全覆盖**:
    *   🎥 **文生视频 (Text-to-Video)**
    *   🖼️ **图生视频 (Image-to-Video)**: 支持输入单张起幅图片。
    *   🎞️ **多图生视频 (Multi-Image-to-Video)**: 支持输入多张图片，自动构建平滑转场。
    *   🎬 **首尾帧生视频 (Keyframes-to-Video)**: 支持精确控制首尾关键帧（起幅与止幅）。
    *   *系统会根据模式自动推荐最佳的 Prompt（提示词）。*
*   **无限轮询与异步排队**: 完美适配视频生成的耗时特性。界面提供动态的无限进度指示器，每 10 秒自动查询一次任务状态，彻底解放人工等待。
*   **自动解析播放**: 任务完成后，自动提取 `remixed_from_video_id` 并在界面中展开播放。

### 4. 👨‍💻 开发者专属工具
*   **实时 cURL 生成器**: 界面调整参数时，动态且实时地生成对应的 `cURL` 命令行。针对超长 Base64 数据还会自动做截断展示，避免浏览器卡死。
*   **无硬编码密钥**: 支持通过侧边栏密码框安全输入，或读取操作系统的环境变量。
*   **本地 Debug 日志**: 每次图片生成请求后，自动在本地保存 `debug_response.json`，方便底层数据追溯。

---

## 🛠️ 安装与运行指南

### 环境要求
*   Python 3.8 或以上版本
*   Git

### 1. 克隆项目
```bash
git clone https://github.com/adamli008/llm-test.git
cd llm-test
```

### 2. 创建并激活虚拟环境 (强烈推荐)
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 启动应用
**方式一：快捷脚本启动（推荐）**
如果你是 macOS 或 Linux 用户，直接运行项目内自带的快捷脚本即可：
```bash
./run.sh
```

**方式二：标准启动**
```bash
streamlit run app.py
```
运行后，默认浏览器会自动打开 `http://localhost:8501`。

---

## 🔐 配置 API Key

代码中不包含硬编码的 Token。你有两种方式提供 API Key：

> 🔑 **如何获取 API Key？**
> 请前往 Agnes AI 开放平台申请您的专属 API Key：
> [https://platform.agnes-ai.com/settings/apiKeys](https://platform.agnes-ai.com/settings/apiKeys)

**方式一：界面输入**
启动应用后，左侧边栏会提示“请先配置 API Key”。填入你的 `sk-...` 密钥回车即可。密钥仅存在于当前浏览器内存中。

**方式二：环境变量**
在启动应用前配置环境变量，可以跳过页面的密码验证：
```bash
export AGNES_API_KEY="sk-你的真实API_KEY"
./run.sh
```

---

## 💡 常见问题 (FAQ)

**Q: 执行 `git push` 时报错 `Failed to connect to github.com port 443` 怎么办？**
A: 这是国内网络导致 Git 无法直连 GitHub。如果使用代理软件（如 Clash，默认端口 7890），可在终端为 Git 设置本地代理：
```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```
推送完成后，取消代理命令为：
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```