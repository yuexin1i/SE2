import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import csv
import os
from datetime import datetime

DATA_FILE = 'expenses.csv'

# === 清新明亮配色方案 ===
BG_COLOR = "#f5f7fa"              # 淺灰藍背景
CARD_BG = "#ffffff"               # 純白卡片
ACCENT_PRIMARY = "#2563eb"        # 藍色（主要）
ACCENT_LIGHT = "#3b82f6"          # 淺藍色
SUCCESS_COLOR = "#10b981"         # 翠綠
SUCCESS_LIGHT = "#34d399"         
WARNING_COLOR = "#f59e0b"         # 橘黃
DANGER_COLOR = "#ef4444"          # 紅色
TEXT_PRIMARY = "#1e293b"          # 深灰文字
TEXT_SECONDARY = "#64748b"        # 次要文字
BORDER_COLOR = "#e2e8f0"          # 邊框
INPUT_BG = "#f8fafc"              # 輸入框背景

FONT_TITLE = ("Arial", 26, "bold")
FONT_SUBTITLE = ("Arial", 10)
FONT_LABEL = ("Arial", 10, "bold")
FONT_INPUT = ("Arial", 11)
FONT_BUTTON = ("Arial", 12, "bold")
# ========================

def save_expense(date_entry, amount_entry, category_var, note_entry, status_label, save_btn):
    date = date_entry.get_date().strftime("%Y-%m-%d")
    amount = amount_entry.get().strip()
    category = category_var.get().split()[-1]  # 移除 emoji
    note = note_entry.get().strip()

    if not amount:
        messagebox.showwarning("提示", "金額不能為空！")
        amount_entry.focus()
        return

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的金額數字！")
        amount_entry.focus()
        return

    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Date', 'Amount', 'Category', 'Note'])
            writer.writerow([date, amount, category, note])
        
        # 成功動畫
        amount_entry.delete(0, tk.END)
        note_entry.delete(0, tk.END)
        
        # 按鈕動畫
        original_text = save_btn.cget("text")
        save_btn.config(text="✓ 儲存成功", bg=SUCCESS_COLOR)
        
        status_label.config(
            text=f"✓ 已記錄 ${amount_val:,.0f} 於 {category} 類別", 
            fg=SUCCESS_COLOR
        )
        
        def reset_ui():
            save_btn.config(text=original_text, bg=ACCENT_PRIMARY)
            status_label.config(text="")
            amount_entry.focus()
        
        status_label.after(3000, reset_ui)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"存檔失敗: {e}")

class StylishEntry(tk.Frame):
    """美化輸入框"""
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, bg=CARD_BG)
        
        # 容器
        self.container = tk.Frame(self, bg=INPUT_BG, highlightbackground=BORDER_COLOR,
                                 highlightthickness=2, highlightcolor=ACCENT_LIGHT)
        self.container.pack(fill="both", expand=True)
        
        # 輸入框
        self.entry = tk.Entry(
            self.container,
            font=FONT_INPUT,
            bg=INPUT_BG,
            fg=TEXT_PRIMARY,
            relief="flat",
            insertbackground=ACCENT_PRIMARY,
            bd=0,
            **kwargs
        )
        self.entry.pack(padx=14, pady=11, fill="both", expand=True)
        
        # 焦點效果
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, e):
        self.container.config(highlightcolor=ACCENT_PRIMARY, highlightbackground=ACCENT_PRIMARY)
    
    def _on_focus_out(self, e):
        self.container.config(highlightcolor=ACCENT_LIGHT, highlightbackground=BORDER_COLOR)
    
    def get(self):
        return self.entry.get()
    
    def delete(self, first, last):
        self.entry.delete(first, last)
    
    def focus(self):
        self.entry.focus()

def run_gui():
    window = tk.Tk()
    window.title("💰 精緻記帳工具")
    window.geometry("520x700")
    window.configure(bg=BG_COLOR)
    
    # 設定 DPI
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    window.geometry("+80+80")
    window.resizable(False, False)

    # === 主容器 ===
    container = tk.Frame(window, bg=BG_COLOR)
    container.pack(fill="both", expand=True, padx=25, pady=25)

    # === 頂部裝飾條 ===
    top_bar = tk.Frame(container, bg=ACCENT_PRIMARY, height=6)
    top_bar.pack(fill="x")

    # === 主卡片 ===
    card = tk.Frame(container, bg=CARD_BG, relief="solid", borderwidth=1, 
                   highlightbackground=BORDER_COLOR, highlightthickness=0)
    card.pack(fill="both", expand=True)

    # === 頭部區域 ===
    header = tk.Frame(card, bg=CARD_BG)
    header.pack(fill="x", padx=35, pady=(35, 5))
    
    # 圖標 + 標題（水平排列）
    title_frame = tk.Frame(header, bg=CARD_BG)
    title_frame.pack()
    
    icon = tk.Label(title_frame, text="💰", font=("Arial", 36), bg=CARD_BG)
    icon.pack(side="left", padx=(0, 12))
    
    title_text = tk.Frame(title_frame, bg=CARD_BG)
    title_text.pack(side="left")
    
    tk.Label(title_text, text="記帳工具", font=FONT_TITLE, 
            bg=CARD_BG, fg=TEXT_PRIMARY).pack(anchor="w")
    
    tk.Label(title_text, text="輕鬆管理每一筆支出", 
            font=FONT_SUBTITLE, bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w")

    # 裝飾性分隔線
    separator = tk.Frame(card, bg=BORDER_COLOR, height=1)
    separator.pack(fill="x", padx=35, pady=20)

    # === 表單區域 ===
    form = tk.Frame(card, bg=CARD_BG)
    form.pack(fill="both", padx=35, pady=5)

    # 1. 日期
    date_frame = tk.Frame(form, bg=CARD_BG)
    date_frame.pack(fill="x", pady=(0, 18))
    
    date_label_frame = tk.Frame(date_frame, bg=CARD_BG)
    date_label_frame.pack(fill="x")
    
    tk.Label(date_label_frame, text="📅", font=("Arial", 14), bg=CARD_BG).pack(side="left", padx=(0,6))
    tk.Label(date_label_frame, text="日期", font=FONT_LABEL, 
            bg=CARD_BG, fg=TEXT_PRIMARY).pack(side="left")
    
    date_entry = DateEntry(
        date_frame,
        font=FONT_INPUT,
        background=ACCENT_PRIMARY,
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        locale='zh_TW',
        selectbackground=ACCENT_PRIMARY,
        selectforeground='white',
        headersbackground=ACCENT_PRIMARY,
        headersforeground='white',
        normalbackground=CARD_BG,
        normalforeground=TEXT_PRIMARY,
        weekendbackground=INPUT_BG,
        weekendforeground=ACCENT_PRIMARY,
        relief="solid"
    )
    date_entry.pack(fill="x", pady=(8, 0), ipady=8)

    # 2. 金額
    amount_frame = tk.Frame(form, bg=CARD_BG)
    amount_frame.pack(fill="x", pady=(0, 18))
    
    amount_label_frame = tk.Frame(amount_frame, bg=CARD_BG)
    amount_label_frame.pack(fill="x")
    
    tk.Label(amount_label_frame, text="💵", font=("Arial", 14), bg=CARD_BG).pack(side="left", padx=(0,6))
    tk.Label(amount_label_frame, text="金額", font=FONT_LABEL, 
            bg=CARD_BG, fg=TEXT_PRIMARY).pack(side="left")
    tk.Label(amount_label_frame, text="(必填)", font=("Arial", 9), 
            bg=CARD_BG, fg=DANGER_COLOR).pack(side="left", padx=(5,0))
    
    amount_entry = StylishEntry(amount_frame)
    amount_entry.pack(fill="x", pady=(8, 0))

    # 3. 類別
    cat_frame = tk.Frame(form, bg=CARD_BG)
    cat_frame.pack(fill="x", pady=(0, 18))
    
    cat_label_frame = tk.Frame(cat_frame, bg=CARD_BG)
    cat_label_frame.pack(fill="x")
    
    tk.Label(cat_label_frame, text="🏷️", font=("Arial", 14), bg=CARD_BG).pack(side="left", padx=(0,6))
    tk.Label(cat_label_frame, text="類別", font=FONT_LABEL, 
            bg=CARD_BG, fg=TEXT_PRIMARY).pack(side="left")
    
    categories = ["🍔 食物", "🚗 交通", "🎮 娛樂", "🛍️購物", 
                  "🏠 居住", "💊 醫療", "📦 其他"]
    category_var = tk.StringVar(value=categories[0])
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        "Modern.TCombobox",
        fieldbackground=INPUT_BG,
        background=CARD_BG,
        foreground=TEXT_PRIMARY,
        arrowcolor=ACCENT_PRIMARY,
        bordercolor=BORDER_COLOR,
        lightcolor=INPUT_BG,
        darkcolor=INPUT_BG,
        borderwidth=2,
        relief="solid"
    )
    style.map('Modern.TCombobox',
              fieldbackground=[('readonly', INPUT_BG)],
              foreground=[('readonly', TEXT_PRIMARY)],
              bordercolor=[('focus', ACCENT_PRIMARY)])
    
    cat_combo = ttk.Combobox(
        cat_frame,
        textvariable=category_var,
        values=categories,
        state="readonly",
        font=FONT_INPUT,
        style="Modern.TCombobox"
    )
    cat_combo.pack(fill="x", pady=(8, 0), ipady=9)

    # 4. 備註
    note_frame = tk.Frame(form, bg=CARD_BG)
    note_frame.pack(fill="x", pady=(0, 18))
    
    note_label_frame = tk.Frame(note_frame, bg=CARD_BG)
    note_label_frame.pack(fill="x")
    
    tk.Label(note_label_frame, text="📝", font=("Arial", 14), bg=CARD_BG).pack(side="left", padx=(0,6))
    tk.Label(note_label_frame, text="備註", font=FONT_LABEL, 
            bg=CARD_BG, fg=TEXT_PRIMARY).pack(side="left")
    tk.Label(note_label_frame, text="(選填)", font=("Arial", 9), 
            bg=CARD_BG, fg=TEXT_SECONDARY).pack(side="left", padx=(5,0))
    
    note_entry = StylishEntry(note_frame)
    note_entry.pack(fill="x", pady=(8, 0))

    # === 狀態提示 ===
    status_label = tk.Label(card, text="", font=("Arial", 10),
                           bg=CARD_BG, fg=SUCCESS_COLOR, height=2)
    status_label.pack(fill="x", padx=35, pady=(5, 0))

    # === 儲存按鈕 ===
    btn_container = tk.Frame(card, bg=CARD_BG)
    btn_container.pack(fill="x", padx=35, pady=(0, 30))

    def on_btn_enter(e):
        save_btn.config(bg=ACCENT_LIGHT)
    
    def on_btn_leave(e):
        save_btn.config(bg=ACCENT_PRIMARY)

    save_btn = tk.Button(
        btn_container,
        text="💾  儲存記錄",
        font=FONT_BUTTON,
        bg=ACCENT_PRIMARY,
        fg="white",
        activebackground=ACCENT_LIGHT,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        bd=0,
        command=lambda: save_expense(date_entry, amount_entry, category_var,
                                    note_entry, status_label, save_btn)
    )
    save_btn.pack(fill="x", ipady=16)
    save_btn.bind("<Enter>", on_btn_enter)
    save_btn.bind("<Leave>", on_btn_leave)

    # === 底部資訊 ===
    footer = tk.Frame(card, bg=CARD_BG)
    footer.pack(fill="x", pady=(0, 25))
    
    tk.Label(footer, text="💡 圖表會即時更新", 
            font=("Arial", 9), bg=CARD_BG, fg=TEXT_SECONDARY).pack()

    # 預設焦點
    amount_entry.focus()

    window.mainloop()

if __name__ == "__main__":
    run_gui()