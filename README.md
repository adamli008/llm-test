# 🚀 AI 模型综合测试台 (AI Model Tester)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

这是一个基于 **Streamlit** 构建的轻量级、现代化的 Web 应用程序，专门用于快速测试大语言模型（LLM）、图像生成模型以及视频生成模型。

它将原本繁琐的终端 `cURL` 请求转化为直观的图形用户界面 (GUI)，让 AI 接口的调试和效果验证变得前所未有地简单。

---

## ✨ 核心功能亮点

### 1. 💬 对话模型 (Chat Completions)
*   **支持模型**: 默认配置 `agnes-2.0-flash`。
*   **特性**: 快速验证文本生成与对话能力，响应结果清晰渲染，支持长文本阅读。

### 2. 🎨 图片模型 (Image Generations)
*   **支持模型**: 默认配置 `agnes-image-2.1-flash`。
*   **特性**: 
    *   **人性化尺寸选择**: 抛弃繁琐的像素输入，提供直观的比例选择（1:1 方形、16:9 横屏、9:16 竖屏）。
    *   **智能联动**: 选择比例后自动推荐该比例下的 5 种典型分辨率（从基础到极清）。
    *   **容错处理**: 自动检测并修复 API 返回结果中可能缺失的 `https://` 协议头，确保图片能在网页中完美预览。

### 3. 🎬 视频模型 (Video Generations)
*   **支持模型**: 默认配置 `agnes-video-v2.0`。
*   **特性**:
    *   **异步任务处理**: 完美适配视频生成的“提交任务 -> 轮询排队 -> 获取结果”的异步工作流。
    *   **实时状态反馈**: 界面提供动态的进度指示器，每 10 秒自动查询任务状态。
    *   **自动解析播放**: 任务完成后，自动从返回的 JSON 中精准提取 `remixed_from_video_id` 视频链接，并直接在界面中展开播放。

### 4. 👨‍💻 开发者专属工具
*   **实时 cURL 生成器**: 当你在界面上调整任何参数（修改提示词、切换分辨率等），界面下方会自动、实时生成对应的标准 `cURL` 命令行。你可以一键复制，直接粘贴到终端或代码中使用。
*   **JSON 调试面板**: 每次请求后，无论成功或失败，都会提供一个可折叠的原始 JSON 数据面板，方便开发者核对底层字段。
*   **无硬编码密钥**: 彻底杜绝 API Key 泄露风险！支持通过侧边栏密码框安全输入，或读取操作系统的环境变量。

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

# 激活虚拟环境 (Windows)
# venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 启动应用
```bash
streamlit run app.py
```
运行后，你的默认浏览器会自动打开 `http://localhost:8501`。

---

## 🔐 配置 API Key

为了保护你的账户安全，代码中没有硬编码任何 Token。你有两种方式提供 API Key：

**方式一：界面输入（最简单）**
启动应用后，左侧边栏会提示“请先配置 API Key”。在密码框中填入你的 `sk-...` 密钥，按下回车即可解锁全部界面。此方式密钥只存在于当前浏览器内存中，刷新后需重新输入，绝对安全。

**方式二：环境变量（最方便）**
如果你不想每次启动都输入，可以在启动应用前，在终端中配置环境变量：
```bash
export AGNES_API_KEY="sk-你的真实API_KEY"
streamlit run app.py
```

---

## 💡 常见问题 (FAQ)

**Q: 执行 `git push` 时报错 `Failed to connect to github.com port 443` 怎么办？**
A: 这是由于国内网络环境导致 Git 无法直连 GitHub。如果你正在使用代理软件（如 Clash，默认端口 7890），可以在终端中为 Git 设置本地代理：
```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```
推送成功后，如需取消代理可执行：
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```