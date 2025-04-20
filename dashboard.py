import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from settings import settings

class Dashboard:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.master.title("TextReader Dashboard")
        self.master.geometry("800x650")
        self.master.resizable(False, False)
        
        # Setup styles
        self._setup_styles()
        
        # Header
        self._create_header()
        
        # Main content
        content_frame = ttk.Frame(self.master, style='Content.TFrame')
        content_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Create two columns
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        # Voice Settings (Left Top)
        voice_frame = ttk.LabelFrame(left_frame, text="Voice Settings", style='Section.TLabelframe')
        voice_frame.pack(fill='x', pady=10)
        
        # Speech Rate
        ttk.Label(voice_frame, text="Speech Rate:", style='Content.TLabel').pack(anchor='w', padx=15, pady=5)
        self.speed_frame = ttk.Frame(voice_frame)
        self.speed_frame.pack(fill='x', padx=15, pady=5)
        
        self.speed_scale = ttk.Scale(
            self.speed_frame, 
            from_=0.5, 
            to=2.0, 
            value=self.app.tts.speed,
            command=self._update_speed
        )
        self.speed_scale.pack(side='left', fill='x', expand=True)
        self.speed_label = ttk.Label(self.speed_frame, text=f"{self.app.tts.speed:.1f}x", style='Content.TLabel')
        self.speed_label.pack(side='right', padx=5)
        
        # Volume
        ttk.Label(voice_frame, text="Volume:", style='Content.TLabel').pack(anchor='w', padx=15, pady=5)
        self.vol_frame = ttk.Frame(voice_frame)
        self.vol_frame.pack(fill='x', padx=15, pady=5)
        
        self.vol_scale = ttk.Scale(
            self.vol_frame,
            from_=0,
            to=100,
            value=self.app.tts.volume,
            command=self._update_volume
        )
        self.vol_scale.pack(side='left', fill='x', expand=True)
        self.vol_label = ttk.Label(self.vol_frame, text=f"{self.app.tts.volume}%", style='Content.TLabel')
        self.vol_label.pack(side='right', padx=5)
        
        # Test Voice button
        ttk.Button(
            voice_frame,
            text="Test Voice",
            command=lambda: self.app.tts.convert("This is a test of the text to speech system"),
            style='Accent.TButton'
        ).pack(pady=10)
        
        # Language Settings (Right Top)
        lang_frame = ttk.LabelFrame(right_frame, text="Language Settings", style='Section.TLabelframe')
        lang_frame.pack(fill='x', pady=10)
        
        ttk.Label(lang_frame, text="Select Language:", style='Content.TLabel').pack(anchor='w', padx=15, pady=5)
        
        self.lang_var = tk.StringVar(value=self.app.current_lang)
        ttk.Radiobutton(
            lang_frame,
            text="English",
            variable=self.lang_var,
            value="en",
            command=self._set_language,
            style='Language.TRadiobutton'
        ).pack(fill='x', padx=15, pady=5)
        
        ttk.Radiobutton(
            lang_frame,
            text="Arabic",
            variable=self.lang_var,
            value="ar",
            command=self._set_language,
            style='Language.TRadiobutton'
        ).pack(fill='x', padx=15, pady=5)
        
        # Hotkey Configuration (Left Bottom)
        hotkey_frame = ttk.LabelFrame(left_frame, text="Hotkey Configuration", style='Section.TLabelframe')
        hotkey_frame.pack(fill='both', expand=True, pady=10)
        
        self.hotkey_entries = {}
        hotkeys = [
            ("Select Text Area", "select_area", "ctrl+shift+c"),
            ("Read Selected Text", "read_text", "ctrl+shift+v"),
            ("Toggle Language", "toggle_lang", "ctrl+shift+l"),
            ("Show Dashboard", "show_dashboard", "ctrl+shift+d")
        ]
        
        for i, (label, key, default) in enumerate(hotkeys):
            ttk.Label(hotkey_frame, text=label + ":", style='Content.TLabel').pack(anchor='w', padx=15, pady=5)
            entry = ttk.Entry(hotkey_frame, width=30)
            entry.insert(0, settings.get('Hotkeys', key, fallback=default))
            entry.pack(fill='x', padx=15, pady=5)
            self.hotkey_entries[key] = entry
        
        # Save All button inside hotkey_frame
        ttk.Button(
            hotkey_frame,
            text="Save All",
            command=self._save_all_settings,
            style='Success.TButton'
        ).pack(pady=10)
        
        # About Section (Right Bottom)
        about_frame = ttk.LabelFrame(right_frame, text="About", style='Section.TLabelframe')
        about_frame.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(
            about_frame,
            text="TextReader",
            style='Title.TLabel'
        ).pack(pady=10)
        
        ttk.Label(
            about_frame,
            text="Screen Reader with OCR & TTS",
            style='Content.TLabel'
        ).pack()
        
        ttk.Label(
            about_frame,
            text="\nDeveloped with Python using:",
            style='Content.TLabel'
        ).pack(pady=5)
        
        features = [
            "• Tesseract OCR for text recognition",
            "• Edge TTS for speech synthesis",
            "• Tkinter for the user interface"
        ]
        
        for feature in features:
            ttk.Label(
                about_frame,
                text=feature,
                style='Content.TLabel'
            ).pack(pady=2)

    def _setup_styles(self):
        style = ttk.Style()
        
        # Define colors
        bg_color = '#1e1e1e'
        fg_color = '#ffffff'
        
        # Header styles
        style.configure('Header.TFrame', background=bg_color)
        style.configure('Header.TLabel',
            background=bg_color,
            foreground=fg_color,
            font=('Arial', 20, 'bold')
        )
        
        # Content styles
        style.configure('Content.TFrame', background=bg_color)
        style.configure('Content.TLabel',
            background=bg_color,
            foreground=fg_color
        )
        
        # Section styles
        style.configure('Section.TLabelframe',
            background=bg_color,
            foreground=fg_color
        )
        style.configure('Section.TLabelframe.Label',
            background=bg_color,
            foreground=fg_color,
            font=('Arial', 10, 'bold')
        )
        
        # Title style
        style.configure('Title.TLabel',
            background=bg_color,
            foreground=fg_color,
            font=('Arial', 16, 'bold')
        )
        
        # Button styles
        style.configure('Accent.TButton',
            padding=5
        )
        
        style.configure('Success.TButton',
            padding=5
        )
        
        # Radio button style
        style.configure('Language.TRadiobutton',
            background=bg_color,
            foreground=fg_color
        )

    def _create_header(self):
        header_frame = ttk.Frame(self.master, style='Header.TFrame')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="TextReader Dashboard",
            style='Header.TLabel'
        )
        title_label.pack(side='left')
        
        version_label = ttk.Label(
            header_frame,
            text="v1.0.0",
            style='Header.TLabel',
            font=('Arial', 12)
        )
        version_label.pack(side='left', padx=10, pady=3)

    def _update_speed(self, v):
        speed = float(v)
        self.speed_label.config(text=f"{speed:.1f}x")
        self.app.tts.speed = speed
        settings.set('TTS', 'speed', str(speed))

    def _update_volume(self, v):
        vol = int(float(v))
        self.vol_label.config(text=f"{vol}%")
        self.app.tts.volume = vol
        settings.set('TTS', 'volume', str(vol))

    def _set_language(self):
        selected_lang = self.lang_var.get()
        if self.app.current_lang != selected_lang:
            self.app.set_language(selected_lang)

    def _save_all_settings(self):
        # Save hotkeys
        for key, entry in self.hotkey_entries.items():
            settings.set('Hotkeys', key, entry.get())
        
        # Save TTS settings
        settings.set('TTS', 'speed', str(self.app.tts.speed))
        settings.set('TTS', 'volume', str(self.app.tts.volume))
        
        # Save language setting
        settings.set('General', 'language', self.lang_var.get())
        
        # Restart hotkeys
        self.app.register_hotkeys()
        
        # Show confirmation
        self._show_save_confirmation()

    def _show_save_confirmation(self):
        confirm_label = ttk.Label(
            self.master,
            text="Settings saved successfully!",
            style='Success.TLabel'
        )
        confirm_label.pack(pady=5)
        self.master.after(2000, confirm_label.destroy)

    def show(self):
        self.master.mainloop()
