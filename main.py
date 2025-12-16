import subprocess
import sys
import time
import os

def check_dependencies():
    """檢查必要套件是否已安裝"""
    print("🔍 檢查相依套件...")
    
    missing = []
    
    try:
        import tkcalendar
        print("  ✓ tkcalendar 已安裝")
    except ImportError:
        missing.append('tkcalendar')
        print("  ✗ tkcalendar 未安裝")
    
    try:
        import matplotlib
        print("  ✓ matplotlib 已安裝")
    except ImportError:
        missing.append('matplotlib')
        print("  ✗ matplotlib 未安裝")
    
    if missing:
        print(f"\n⚠️  缺少套件: {', '.join(missing)}")
        print("\n請執行以下指令安裝：")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("✅ 所有套件都已安裝\n")
    return True

def main():
    print("=" * 50)
    print("🚀 正在啟動記帳系統...")
    print("=" * 50)
    
    # 檢查套件
    if not check_dependencies():
        input("\n按 Enter 結束...")
        return
    
    # 取得目前 python 執行檔的路徑
    python_exe = sys.executable

    # 1. 啟動圓餅圖視窗
    try:
        p_viz = subprocess.Popen(
            [python_exe, 'create_pie_chart.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ 圖表視窗已啟動")
        time.sleep(1.5)
    except Exception as e:
        print(f"❌ 圖表視窗啟動失敗: {e}")
        return

    # 2. 啟動輸入介面視窗
    try:
        p_input = subprocess.Popen(
            [python_exe, 'input_module.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ 輸入視窗已啟動")
        time.sleep(0.5)
    except Exception as e:
        print(f"❌ 輸入視窗啟動失敗: {e}")
        p_viz.terminate()
        return
    time.sleep(1)
    
    if p_input.poll() is not None:
        # 程序已經結束，讀取錯誤訊息
        stderr = p_input.stderr.read().decode('utf-8', errors='ignore')
        print("\n❌ 輸入視窗啟動後立即關閉！")
        if stderr:
            print("\n錯誤訊息：")
            print(stderr)
        else:
            print("可能是缺少 tkcalendar 套件，請執行: pip install tkcalendar")
        p_viz.terminate()
        input("\n按 Enter 結束...")
        return

    print("\n" + "=" * 50)
    print("✨ 系統運行中... 請在視窗中操作")
    print("💡 若要結束，請直接關閉兩個視窗")
    print("=" * 50 + "\n")

    # 等待兩個視窗都被關閉
    try:
        p_viz.wait()
        p_input.wait()
    except KeyboardInterrupt:
        print("\n⚠️  正在關閉系統...")
        p_viz.terminate()
        p_input.terminate()
    
    print("\n👋 系統已結束。")

if __name__ == "__main__":
    main()