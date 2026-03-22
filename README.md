# AI-TTS 语音合成工具

基于阿里云 CosyVoice 语音合成服务的桌面应用，支持多种语音模型和音色。

## 功能特性

- 🎙️ 多种语音模型支持（CosyVoice v1.5 - v3.5）
- 🗣️ 丰富的内置音色（男声/女声/童声）
- ⚙️ API Key、模型、语音ID 可视化配置
- 📁 自动保存音频到本地
- ▶️ 一键播放生成的音频

## 安装使用

### 方式一：直接运行 exe（Windows）

下载 `dist/AI-TTS.exe`，双击运行即可。

### 方式二：Python 源码运行

```bash
# 安装依赖
pip install dashscope

# 运行
python tts_gui.py
```

### Mac / Linux 用户

```bash
# 安装依赖
pip3 install dashscope pyinstaller

# 运行
python3 tts_gui.py

# 如需打包为应用
pyinstaller --onefile --windowed --name "AI-TTS" tts_gui.py
```

## 配置说明

1. 获取阿里云 API Key
   - 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
   - 开通服务并创建 API Key

2. 在应用中填入 API Key，选择模型和语音ID

3. 输入文本，点击"开始合成"

## 支持的语音

| 语音ID | 名称 | 类型 |
|--------|------|------|
| longxiaochun | 龙小春 | 女声-甜美 |
| longwan | 龙婉 | 女声-温柔 |
| longyue | 龙悦 | 女声-活泼 |
| longfei | 龙飞 | 女声-知性 |
| longjielidou | 龙杰力豆 | 童声 |
| longxiaobai | 龙小白 | 男声-活泼 |
| longyao | 龙尧 | 男声-沉稳 |
| longteng | 龙腾 | 男声-磁性 |

更多音色请参考 [阿里云语音合成文档](https://help.aliyun.com/document_detail/84435.html)。

## 项目结构

```
AI-TTS/
├── tts_gui.py        # 主程序
├── requirements.txt  # 依赖列表
├── run.bat           # Windows 启动脚本
├── config.json       # 配置文件（自动生成）
└── output/           # 音频输出目录（自动创建）
```

## 依赖

- Python 3.8+
- dashscope
- tkinter（Python 内置）

## 许可证

MIT License