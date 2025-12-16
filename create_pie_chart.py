import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button
import csv
import os
import platform
from collections import defaultdict
from datetime import datetime

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
wedge_info = []
current_month = None  # None 代表顯示全部
available_months = []
btn_prev = None
btn_next = None
btn_all = None
month_text = None

def read_data(filter_month=None):
    """讀取消費資料,可選擇性篩選月份"""
    categories = {}
    records = defaultdict(list)
    all_months = set()
    
    if not os.path.isfile(DATA_FILE):
        return categories, records, []
    
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    amount = float(row['Amount'])
                    cat = row['Category'].split()[-1] if ' ' in row['Category'] else row['Category']
                    date_str = row.get('Date', '')
                    note = row.get('Note', '')
                    
                    # 解析日期
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            month_key = date_obj.strftime('%Y-%m')
                            all_months.add(month_key)
                            
                            # 如果有篩選月份,只保留該月份的資料
                            if filter_month and month_key != filter_month:
                                continue
                        except:
                            pass
                    
                    categories[cat] = categories.get(cat, 0) + amount
                    records[cat].append({
                        'date': date_str,
                        'amount': amount,
                        'note': note
                    })
                except:
                    continue
    except:
        pass
    
    # 排序月份(最新的在前)
    sorted_months = sorted(list(all_months), reverse=True)
    
    return categories, records, sorted_months

def update_month_display():
    """更新月份顯示文字"""
    global month_text, current_month
    if month_text:
        if current_month:
            # 轉換成中文顯示
            year, month = current_month.split('-')
            display_text = f"{year} 年 {int(month)} 月"
        else:
            display_text = "全部月份"
        month_text.set_text(display_text)
        fig.canvas.draw_idle()

def on_prev_month(event):
    """切換到上一個月"""
    global current_month, available_months
    
    if not available_months:
        show_no_data_message()
        return
    
    if current_month is None:
        current_month = available_months[0]
    else:
        try:
            idx = available_months.index(current_month)
            if idx < len(available_months) - 1:
                current_month = available_months[idx + 1]
            else:
                # 已經是最早的月份
                show_month_boundary_message("已經是最早的月份了")
                return
        except:
            current_month = available_months[0]
    
    update_month_display()

def on_next_month(event):
    """切換到下一個月"""
    global current_month, available_months
    
    if not available_months:
        show_no_data_message()
        return
    
    if current_month is None:
        current_month = available_months[0]
    else:
        try:
            idx = available_months.index(current_month)
            if idx > 0:
                current_month = available_months[idx - 1]
            else:
                # 已經是最新的月份
                show_month_boundary_message("已經是最新的月份了")
                return
        except:
            current_month = available_months[0]
    
    update_month_display()

def show_no_data_message():
    """顯示無資料訊息"""
    global month_text
    if month_text:
        original_text = month_text.get_text()
        month_text.set_text("尚無任何記帳資料")
        month_text.set_color('#ef4444')
        fig.canvas.draw_idle()
        
        def reset_text():
            month_text.set_text(original_text)
            month_text.set_color(TEXT_COLOR)
            fig.canvas.draw_idle()
        
        # 2秒後恢復
        fig.canvas.manager.window.after(2000, reset_text)

def show_month_boundary_message(message):
    """顯示月份邊界訊息"""
    global month_text
    if month_text:
        original_text = month_text.get_text()
        original_color = month_text.get_color()
        month_text.set_text(message)
        month_text.set_color('#f59e0b')
        fig.canvas.draw_idle()
        
        def reset_text():
            month_text.set_text(original_text)
            month_text.set_color(original_color)
            fig.canvas.draw_idle()
        
        # 1.5秒後恢復
        fig.canvas.manager.window.after(1500, reset_text)

def on_show_all(event):
    """顯示全部月份"""
    global current_month
    current_month = None
    update_month_display()

def on_click(event):
    """點擊事件處理(使用 Matplotlib 內建判定)"""
    global selected_category, ax_detail, wedge_info
    
    if event.inaxes != ax_pie:
        return
    
    # 使用 Matplotlib 內建的 contains 方法(最準確)
    for category, wedge in wedge_info:
        contains, _ = wedge.contains(event)
        if contains:
            selected_category = category
            show_detail(category)
            print(f"點擊了: {category}")
            break

def show_detail(category):
    """顯示類別詳細資料"""
    global ax_detail, detail_records, current_month
    
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
    month_info = ""
    if current_month:
        year, month = current_month.split('-')
        month_info = f" - {year}/{month}"
    
    ax_detail.text(0.5, 0.945, f"【 {category}{month_info} 】", 
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
    max_display = 12
    
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
        
        # 金額(右對齊)
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
    global current_data, detail_records, ax_pie, wedge_info, available_months
    
    data, records, months = read_data(current_month)
    current_data = data
    detail_records = records
    available_months = months
    wedge_info = []
    
    ax_pie.clear()
    
    if not data:
        empty_text = "等待資料中...\n\n請在輸入視窗新增消費"
        if current_month and available_months:
            year, month = current_month.split('-')
            empty_text = f"{year} 年 {int(month)} 月\n\n尚無消費記錄"
        
        ax_pie.text(0.5, 0.5, empty_text,
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
    
    # 儲存扇形資訊
    for label, wedge in zip(labels, wedges):
        wedge_info.append((label, wedge))
    
    # 美化文字
    plt.setp(autotexts, size=11, weight="bold", color="white")
    plt.setp(texts, size=13, weight="bold")
    
    # 計算總金額
    total_amount = sum(sizes)
    
    # 標題
    title_text = '各類別消費占比\n點擊區塊查看詳細記錄'
    if current_month:
        year, month = current_month.split('-')
        title_text = f'{year} 年 {int(month)} 月消費占比\n總支出: ${total_amount:,.0f}  |  點擊區塊查看詳細'
    else:
        title_text = f'全部消費占比\n總支出: ${total_amount:,.0f}  |  點擊區塊查看詳細'
    
    ax_pie.set_title(title_text, fontsize=15, fontweight='bold',pad=0, color=TEXT_COLOR)
    
    # 保持選中狀態
    if selected_category and selected_category in data:
        show_detail(selected_category)

def run_chart():
    """啟動圖表視窗"""
    global fig, ax_pie, ax_detail, btn_prev, btn_next, btn_all, month_text
    
    # 建立高解析度視窗
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 100
    
    fig = plt.figure(figsize=(16, 8.5))
    fig.canvas.manager.set_window_title('即時消費分析 - 月份篩選')
    fig.patch.set_facecolor(BG_COLOR)
    
    # === 月份控制列(調整到圓餅圖正上方) ===
    # 上一月按鈕
    ax_btn_prev = plt.axes([0.00, 0.94, 0.09, 0.035])
    btn_prev = Button(ax_btn_prev, '< 上一月', color='#e8eaf0', hovercolor='#d0d5dd')
    btn_prev.label.set_fontsize(10)
    btn_prev.on_clicked(on_prev_month)
    
    # 顯示全部按鈕
    ax_btn_all = plt.axes([0.10, 0.94, 0.09, 0.035])
    btn_all = Button(ax_btn_all, '顯示全部', color='#5B7FFF', hovercolor='#7d96ff')
    btn_all.label.set_color('white')
    btn_all.label.set_fontsize(10)
    btn_all.on_clicked(on_show_all)
    
    # 月份顯示(在圓餅圖正上方中間)
    month_text = fig.text(0.275, 0.968, '全部月份', ha='center', va='center',
                         fontsize=13, fontweight='bold', color=TEXT_COLOR,
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                                 edgecolor='#d0d5dd', linewidth=1.5))
    
    # 下一月按鈕
    ax_btn_next = plt.axes([0.35, 0.94, 0.09, 0.035])
    btn_next = Button(ax_btn_next, '下一月 >', color='#e8eaf0', hovercolor='#d0d5dd')
    btn_next.label.set_fontsize(10)
    btn_next.on_clicked(on_next_month)
    
    # 左側:圓餅圖(調整位置,縮短高度給上方按鈕留空間)
    ax_pie = plt.axes([0.05, 0.05, 0.45, 0.84])
    ax_pie.set_facecolor(CARD_BG)
    
    # 右側:詳細資料(調整位置)
    ax_detail = plt.axes([0.52, 0.05, 0.45, 0.90])
    ax_detail.set_facecolor(BG_COLOR)
    
    # 初始提示
    prompt_rect = Rectangle((0.15, 0.4), 0.7, 0.2,
                           facecolor='white', edgecolor=ACCENT_COLOR,
                           linewidth=2, transform=ax_detail.transAxes)
    ax_detail.add_patch(prompt_rect)
    
    ax_detail.text(0.5, 0.5, "點擊左側圓餅圖\n查看詳細記錄",
                  ha='center', va='center', fontsize=14, color=TEXT_COLOR,
                  transform=ax_detail.transAxes, fontweight='bold')
    ax_detail.axis('off')
    
    # 綁定點擊事件
    fig.canvas.mpl_connect('button_press_event', on_click)
    
    # 調整視窗位置
    try:
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(520, 50, 1300, 700)
    except:
        pass
    
    # 啟動動畫
    ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
    plt.show()

if __name__ == "__main__":
    run_chart()