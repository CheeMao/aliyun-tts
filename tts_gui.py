#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-TTS 语音合成工具
基于阿里云 CosyVoice 语音合成服务
"""

import os
import sys
import json
import threading
from pathlib import Path
from datetime import datetime

# GUI
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

# TTS
try:
    import dashscope
    from dashscope.audio.tts_v2 import SpeechSynthesizer
except ImportError:
    print("请先安装 dashscope: pip install dashscope")
    sys.exit(1)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.json"
OUTPUT_DIR = Path(__file__).parent / "output"


class TTSGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI-TTS 语音合成工具")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # 加载配置
        self.config = self.load_config()

        # 设置 API Key
        if self.config.get("api_key"):
            dashscope.api_key = self.config["api_key"]
            dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
            dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

        # 创建输出目录
        OUTPUT_DIR.mkdir(exist_ok=True)

        # 构建界面
        self.build_ui()

    def load_config(self):
        """加载配置"""
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
            except:
                return {}
        return {}

    def save_config(self):
        """保存配置"""
        CONFIG_FILE.write_text(json.dumps(self.config, ensure_ascii=False, indent=2), encoding='utf-8')

    def build_ui(self):
        """构建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === 配置区域 ===
        config_frame = ttk.LabelFrame(main_frame, text="配置", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # API Key
        ttk.Label(config_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        self.api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10))
        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="显示", variable=self.show_key_var,
                        command=lambda: self.api_key_entry.configure(show="" if self.show_key_var.get() else "*")).grid(row=0, column=2)

        # 模型选择
        ttk.Label(config_frame, text="模型:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.model_var = tk.StringVar(value=self.config.get("model", "cosyvoice-v3.5-plus"))
        model_combo = ttk.Combobox(config_frame, textvariable=self.model_var, width=47)
        model_combo['values'] = (
            "cosyvoice-v3.5-plus",      # 最新高质量模型
            "cosyvoice-v3.5-32k",       # 32k采样率
            "cosyvoice-v2.5-plus",      # v2.5版本
            "cosyvoice-v1.5-plus",      # v1.5版本
        )
        model_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

        # 语音ID
        ttk.Label(config_frame, text="语音ID:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.voice_var = tk.StringVar(value=self.config.get("voice_id", "longxiaochun"))
        voice_combo = ttk.Combobox(config_frame, textvariable=self.voice_var, width=47)
        voice_combo['values'] = (
            # 女声
            "longxiaochun",      # 龙小春 - 甜美女声
            "longwan",           # 龙婉 - 温柔女声
            "longyue",           # 龙悦 - 活泼女声
            "longfei",           # 龙飞 - 知性女声
            "longjielidou",      # 龙杰力豆 - 童声
            "longshuo",          # 龙硕 - 播音女声
            "longshu",           # 龙姝 - 温婉女声
            # 男声
            "longxiaobai",       # 龙小白 - 活泼男声
            "longyao",           # 龙尧 - 沉稳男声
            "longteng",          # 龙腾 - 磁性男声
            "longshuo_male",     # 龙硕 - 播音男声
        )
        voice_combo.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))

        # 保存配置按钮
        ttk.Button(config_frame, text="保存配置", command=self.save_config_clicked).grid(row=3, column=1, sticky=tk.W, pady=(10, 0))

        config_frame.columnconfigure(1, weight=1)

        # === 文本输入区域 ===
        text_frame = ttk.LabelFrame(main_frame, text="文本内容", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.text_input = scrolledtext.ScrolledText(text_frame, height=12, wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True)

        # === 操作区域 ===
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        # 输出文件名
        ttk.Label(action_frame, text="输出文件:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_var = tk.StringVar(value=f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
        ttk.Entry(action_frame, textvariable=self.output_var, width=30).pack(side=tk.LEFT, padx=(0, 10))

        # 合成按钮
        self.synthesize_btn = ttk.Button(action_frame, text="开始合成", command=self.synthesize_clicked)
        self.synthesize_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 播放按钮
        self.play_btn = ttk.Button(action_frame, text="播放", command=self.play_audio, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 打开目录按钮
        ttk.Button(action_frame, text="打开输出目录", command=self.open_output_dir).pack(side=tk.LEFT)

        # === 日志区域 ===
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.X)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.X)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, pady=(10, 0))

    def log(self, message):
        """添加日志"""
        self.log_text.configure(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def save_config_clicked(self):
        """保存配置"""
        self.config["api_key"] = self.api_key_var.get().strip()
        self.config["model"] = self.model_var.get()
        self.config["voice_id"] = self.voice_var.get()
        self.save_config()

        # 更新 dashscope 配置
        if self.config["api_key"]:
            dashscope.api_key = self.config["api_key"]
            dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
            dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

        self.log("配置已保存")
        messagebox.showinfo("成功", "配置已保存")

    def synthesize_clicked(self):
        """开始合成"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入要合成的文本")
            return

        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "请配置 API Key")
            return

        # 禁用按钮
        self.synthesize_btn.configure(state=tk.DISABLED)
        self.status_var.set("正在合成...")

        # 在后台线程执行
        thread = threading.Thread(target=self.do_synthesize, args=(text,))
        thread.daemon = True
        thread.start()

    def do_synthesize(self, text):
        """执行合成（后台线程）"""
        try:
            # 设置 API Key
            dashscope.api_key = self.api_key_var.get().strip()
            dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
            dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

            model = self.model_var.get()
            voice = self.voice_var.get()
            output_file = OUTPUT_DIR / self.output_var.get()

            self.log(f"开始合成: 模型={model}, 语音={voice}")
            self.log(f"文本长度: {len(text)} 字符")

            # 创建合成器并调用
            synthesizer = SpeechSynthesizer(model=model, voice=voice)
            audio_data = synthesizer.call(text)

            # 保存音频文件
            output_file.write_bytes(audio_data)

            self.log(f"合成成功: {output_file}")
            self.root.after(0, lambda: self.synthesis_complete(str(output_file)))

        except Exception as e:
            self.log(f"合成失败: {e}")
            self.root.after(0, lambda: self.synthesis_failed(str(e)))

    def synthesis_complete(self, output_file):
        """合成完成"""
        self.synthesize_btn.configure(state=tk.NORMAL)
        self.play_btn.configure(state=tk.NORMAL)
        self.status_var.set(f"合成完成: {output_file}")
        self.last_output_file = output_file
        messagebox.showinfo("成功", f"语音合成完成!\n\n输出文件: {output_file}")

    def synthesis_failed(self, error):
        """合成失败"""
        self.synthesize_btn.configure(state=tk.NORMAL)
        self.status_var.set(f"合成失败: {error}")
        messagebox.showerror("错误", f"语音合成失败:\n{error}")

    def play_audio(self):
        """播放音频"""
        if hasattr(self, 'last_output_file') and os.path.exists(self.last_output_file):
            # 跨平台播放
            if sys.platform == 'win32':
                os.startfile(self.last_output_file)
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                subprocess.run(['open', self.last_output_file])
            else:  # Linux
                import subprocess
                subprocess.run(['xdg-open', self.last_output_file])

    def open_output_dir(self):
        """打开输出目录"""
        OUTPUT_DIR.mkdir(exist_ok=True)
        if sys.platform == 'win32':
            os.startfile(OUTPUT_DIR)
        elif sys.platform == 'darwin':  # macOS
            import subprocess
            subprocess.run(['open', str(OUTPUT_DIR)])
        else:  # Linux
            import subprocess
            subprocess.run(['xdg-open', str(OUTPUT_DIR)])

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    app = TTSGui()
    app.run()


if __name__ == '__main__':
    main()