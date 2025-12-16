import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Wedge
import csv
import os
import platform
from collections import defaultdict
import numpy as np

# --- 字體設定 ---
system_name = platform.system()
if system_name == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
elif system_name == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC']
else:
    plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DATA_FILE = 'expenses.csv'

# --- 精緻配色 ---
COLORS = ['#FF6B9D', '#C44569', '#FFA07A', '#FFD93D', '#6BCF7F', 
          '#4ECDC4', '#5B7FFF', '#A28FDB', '#FF8B94', '#95E1D3']
BG_COLOR = '#f8f9fa'
CARD_BG = '#ffffff'
TEXT_COLOR = '#2c3e50'
ACCENT_COLOR = '#5B7FFF'

# === 全域變數 ===
fig = None
ax_pie = None
ax_detail = None
current_data = {}
detail_records = defaultdict(list)
selected_category = None
wedge_info = []  # 儲存每個扇形的資訊

def read_data():
    """讀取消費資料"""
    categories = {}
    records = defaultdict(list)
    
    if not os.path.isfile(DATA_FILE):
        return categories, records
    
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    amount = float(row['Amount'])
                    cat = row['Category'].split()[-1] if ' ' in row['Category'] else row['Category']
                    date = row.get('Date', '')
                    note = row.get('Note', '')
                    
                    categories[cat] = categories.get(cat, 0) + amount
                    records[cat].append({
                        'date': date,
                        'amount': amount,
                        'note': note
                    })
                except:
                    continue
    except:
        pass
    
    return categories, records

def on_click(event):
    """點擊事件處理（使用 Matplotlib 內建判定）"""
    global selected_category, ax_detail, wedge_info
    
    if event.inaxes != ax_pie:
        return
    
    # 使用 Matplotlib 內建的 contains 方法（最準確）
    for category, wedge in wedge_info:
        # contains 會回傳 (bool, dict)
        contains, _ = wedge.contains(event)
        if contains:
            selected_category = category
            show_detail(category)
            print(f"點擊了: {category}")  # 除錯用
            break

def show_detail(category):
    """顯示類別詳細資料"""
    global ax_detail, detail_records
    
    ax_detail.clear()
    ax_detail.set_facecolor(BG_COLOR)
    
    records = detail_records.get(category, [])
    
    if not records:
        ax_detail.text(0.5, 0.5, "此類別無記錄", 
                      ha='center', va='center', fontsize=14, color='#aaa')
        ax_detail.axis('off')
        fig.canvas.draw_idle()
        return
    
    # === 頭部資訊卡片 ===
    total = sum(r['amount'] for r in records)
    
    # 標題背景
    title_rect = Rectangle((0.05, 0.88), 0.9, 0.1, 
                           facecolor=ACCENT_COLOR, edgecolor='none',
                           transform=ax_detail.transAxes, alpha=0.15)
    ax_detail.add_patch(title_rect)
    
    # 類別名稱
    ax_detail.text(0.5, 0.945, f"【 {category} 】", 
                  ha='center', va='center',
                  fontsize=16, fontweight='bold', color=TEXT_COLOR,
                  transform=ax_detail.transAxes)
    
    # 統計資訊
    stats_text = f"共 {len(records)} 筆  |  總計 ${total:,.0f}"
    ax_detail.text(0.5, 0.895, stats_text,
                  ha='center', va='center',
                  fontsize=11, color='#5a6c7d',
                  transform=ax_detail.transAxes)
    
    # === 記錄列表 ===
    y_pos = 0.82
    max_display = 12  # 最多顯示筆數
    
    sorted_records = sorted(records, key=lambda x: x['date'], reverse=True)[:max_display]
    
    for i, record in enumerate(sorted_records):
        date = record['date']
        amount = record['amount']
        note = record['note'] or '(無備註)'
        
        # 背景卡片
        bg_color = CARD_BG if i % 2 == 0 else BG_COLOR
        card_rect = Rectangle((0.05, y_pos - 0.055), 0.9, 0.055,
                              facecolor=bg_color, edgecolor='#e0e0e0',
                              linewidth=0.8, transform=ax_detail.transAxes)
        ax_detail.add_patch(card_rect)
        
        # 日期
        ax_detail.text(0.08, y_pos - 0.0275, date,
                      ha='left', va='center', fontsize=9.5,
                      color='#5a6c7d', transform=ax_detail.transAxes,
                      fontweight='bold')
        
        # 金額（右對齊）
        ax_detail.text(0.92, y_pos - 0.0275, f"${amount:,.0f}",
                      ha='right', va='center', fontsize=10,
                      color=ACCENT_COLOR, transform=ax_detail.transAxes,
                      fontweight='bold')
        
        # 備註
        if len(note) > 20:
            note = note[:20] + "..."
        ax_detail.text(0.5, y_pos - 0.0275, note,
                      ha='center', va='center', fontsize=9,
                      color='#7a8a9a', transform=ax_detail.transAxes)
        
        y_pos -= 0.065
        
        if y_pos < 0.08:
            break
    
    # 如果有更多記錄
    if len(records) > max_display:
        remaining = len(records) - max_display
        ax_detail.text(0.5, 0.04, f"... 還有 {remaining} 筆記錄",
                      ha='center', va='center', fontsize=9,
                      color='#aaa', transform=ax_detail.transAxes,
                      style='italic')
    
    ax_detail.set_xlim(0, 1)
    ax_detail.set_ylim(0, 1)
    ax_detail.axis('off')
    fig.canvas.draw_idle()

def animate(i):
    """動畫更新函數"""
    global current_data, detail_records, ax_pie, wedge_info
    
    data, records = read_data()
    current_data = data
    detail_records = records
    wedge_info = []
    
    ax_pie.clear()
    
    if not data:
        ax_pie.text(0.5, 0.5, "📊 等待資料中...\n\n請在輸入視窗新增消費",
                   ha='center', va='center', fontsize=16, color='#7f8c8d',
                   bbox=dict(boxstyle='round,pad=1', facecolor='white', 
                           edgecolor='#ddd', linewidth=2))
        ax_pie.axis('off')
        return
    
    labels = list(data.keys())
    sizes = list(data.values())
    
    # Explode 效果
    max_index = sizes.index(max(sizes))
    explode = [0.1 if i == max_index else 0.03 for i in range(len(sizes))]
    
    # 繪製圓餅圖
    wedges, texts, autotexts = ax_pie.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        explode=explode,
        colors=COLORS[:len(sizes)],
        shadow=True,
        textprops={'fontsize': 12, 'color': TEXT_COLOR, 'weight': 'bold'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'antialiased': True}
    )
    
    # 儲存扇形資訊供點擊判定使用
    for label, wedge in zip(labels, wedges):
        wedge_info.append((label, wedge))
    
    # 美化文字
    plt.setp(autotexts, size=11, weight="bold", color="white")
    plt.setp(texts, size=13, weight="bold")
    
    # 標題
    ax_pie.set_title('💰 各類別消費佔比\n👆 點擊區塊查看詳細記錄',
                    fontsize=17, fontweight='bold', pad=25, color=TEXT_COLOR)
    
    # 保持選中狀態
    if selected_category and selected_category in data:
        show_detail(selected_category)

def run_chart():
    """啟動圖表視窗"""
    global fig, ax_pie, ax_detail
    
    # 建立高解析度視窗
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 100
    
    fig = plt.figure(figsize=(15, 7.5))
    fig.canvas.manager.set_window_title('即時消費分析 - 互動式圖表')
    fig.patch.set_facecolor(BG_COLOR)
    
    # 左側：圓餅圖
    ax_pie = plt.subplot(1, 2, 1)
    ax_pie.set_facecolor(CARD_BG)
    
    # 右側：詳細資料
    ax_detail = plt.subplot(1, 2, 2)
    ax_detail.set_facecolor(BG_COLOR)
    
    # 初始提示
    prompt_rect = Rectangle((0.15, 0.4), 0.7, 0.2,
                           facecolor='white', edgecolor=ACCENT_COLOR,
                           linewidth=2, transform=ax_detail.transAxes)
    ax_detail.add_patch(prompt_rect)
    
    ax_detail.text(0.5, 0.5, "👆 點擊左側圓餅圖\n查看詳細記錄",
                  ha='center', va='center', fontsize=14, color=TEXT_COLOR,
                  transform=ax_detail.transAxes, fontweight='bold')
    ax_detail.axis('off')
    
    # 綁定點擊事件
    fig.canvas.mpl_connect('button_press_event', on_click)
    
    # 調整視窗位置
    try:
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(550, 50, 1200, 650)
    except:
        pass
    
    # 啟動動畫
    ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
    plt.tight_layout(pad=2.0)
    plt.show()

if __name__ == "__main__":
    run_chart()