# simulator.py
import matplotlib.pyplot as plt


class Simulator:
    """
    模擬器主程式
    用來執行不同的頁面置換演算法，
    在不同參考字串下比較效能結果。
    """

    def __init__(self):
        """初始化模擬器設定"""
        # 實體記憶體中可用框架（frames）的數量集合
        self.frame_sizes = [30, 60, 90, 120, 150]

        # 儲存所有實驗結果的資料結構
        # 結構如下:
        # results[參考字串名稱][演算法名稱] = { "faults": [...], "interrupts": [...], "writes": [...] }
        self.results = {}

    def run_experiments(self, references, algorithms):
        """
        執行所有實驗，測試不同參考字串與演算法的效能

        參數:
            references: dict
                各種參考字串，例如："Random", "Locality", "Zipf"。
            algorithms: dict
                各種演算法類別，例如："FIFO", "Optimal", "ReferenceBits", "ARC"。
        """

        # 初始化結果儲存結構
        for ref_name in references:
            self.results[ref_name] = {}
            for algo_name in algorithms:
                self.results[ref_name][algo_name] = {
                    "faults": [],  # 頁面錯誤次數
                    "interrupts": [],  # 中斷次數（頁面錯誤 + 寫回磁碟）
                    "writes": [],  # 寫回磁碟次數（當被踢出的頁面是髒頁時）
                }

        print("開始執行...")

        # 依序對每個參考字串執行所有演算法
        for ref_name, ref_string in references.items():
            print(f"\n參考字串使用: {ref_name}...")

            # 針對每個演算法
            for algo_name, algo_class in algorithms.items():
                print(f"  開始執行 {algo_name}...")

                # 測試不同的 frame 數量
                for num_frames in self.frame_sizes:
                    print("    Frame sizes: ", num_frames)

                    # 建立演算法實例，傳入 frame 數量
                    algo = algo_class(num_frames)

                    # 執行演算法，傳入參考字串
                    # 預期回傳 faults, interrupts, writes 三個值
                    faults, interrupts, writes = algo.run(ref_string)

                    # 將結果記錄下來
                    self.results[ref_name][algo_name]["faults"].append(faults)
                    self.results[ref_name][algo_name]["interrupts"].append(interrupts)
                    self.results[ref_name][algo_name]["writes"].append(writes)

    def plot_results(self, algorithms):
        """
        繪製實驗結果圖表，包含：
        1. Page Faults vs Frames
        2. Interrupts vs Frames
        3. Disk Writes vs Frames
        每種參考字串會產生一張圖 (含三個子圖)。
        """

        print("\n開始畫圖")

        # 針對每種參考字串繪圖
        for ref_name in self.results:
            # 建立一個圖像含三個子圖（橫向排列）
            fig, axes = plt.subplots(1, 3, figsize=(15, 4))
            fig.suptitle(ref_name, fontsize=14)

            # --- 第一張圖：Page Faults ---
            for algo_name in algorithms:
                axes[0].plot(
                    self.frame_sizes,
                    self.results[ref_name][algo_name]["faults"],
                    marker="o",
                    label=algo_name,
                )
            axes[0].set_xlabel("Frames")
            axes[0].set_ylabel("Page Faults")
            axes[0].legend()
            axes[0].grid(True)

            # --- 第二張圖：Interrupts ---
            for algo_name in algorithms:
                axes[1].plot(
                    self.frame_sizes,
                    self.results[ref_name][algo_name]["interrupts"],
                    marker="o",
                    label=algo_name,
                )
            axes[1].set_xlabel("Frames")
            axes[1].set_ylabel("Interrupts")
            axes[1].legend()
            axes[1].grid(True)

            # --- 第三張圖：Disk Writes ---
            for algo_name in algorithms:
                axes[2].plot(
                    self.frame_sizes,
                    self.results[ref_name][algo_name]["writes"],
                    marker="o",
                    label=algo_name,
                )
            axes[2].set_xlabel("Frames")
            axes[2].set_ylabel("Disk Writes")
            axes[2].legend()
            axes[2].grid(True)

            # 自動調整子圖間距
            plt.tight_layout()

            # 儲存圖檔
            filename = f'{ref_name.replace(" ", "_")}.png'
            plt.savefig(filename)
            print(f"  存檔: {filename}")

        # 顯示所有圖表
        plt.show()

    def print_summary(self, algorithms):
        """
        印出每個演算法在各參考字串下的平均結果
        包含平均 Page Faults、Interrupts、Disk Writes。
        """

        print("\n=== 實驗結果摘要 ===")

        for ref_name in self.results:
            print(f"\n{ref_name}:")

            for algo_name in algorithms:
                # 計算各項平均值
                avg_faults = sum(self.results[ref_name][algo_name]["faults"]) / len(
                    self.frame_sizes
                )
                avg_interrupts = sum(
                    self.results[ref_name][algo_name]["interrupts"]
                ) / len(self.frame_sizes)
                avg_writes = sum(self.results[ref_name][algo_name]["writes"]) / len(
                    self.frame_sizes
                )

                # 印出平均結果
                print(f"  {algo_name}:")
                print(f"    平均 Page Faults: {avg_faults:.0f}")
                print(f"    平均 Interrupts: {avg_interrupts:.0f}")
                print(f"    平均 Disk Writes: {avg_writes:.0f}")
