# simulator.py
"""
模擬器主程式
負責執行實驗並產生結果
"""
import matplotlib.pyplot as plt


class Simulator:
    """模擬器類別"""

    def __init__(self):
        """初始化模擬器"""
        self.frame_sizes = [30, 60, 90, 120, 150]
        self.results = {}

    def run_experiments(self, references, algorithms):
        """
        執行所有實驗

        參數:
            references: dict, 包含各種參考字串
            algorithms: dict, 包含各種演算法類別
        """
        # 初始化結果儲存結構
        for ref_name in references:
            self.results[ref_name] = {}
            for algo_name in algorithms:
                self.results[ref_name][algo_name] = {
                    "faults": [],
                    "interrupts": [],
                    "writes": [],
                }

        # 執行模擬
        print("開始執行...")
        # 選擇字串參考的生成方式
        for ref_name, ref_string in references.items():
            print(f"\n參考字串使用: {ref_name}...")

            # 選擇演算法
            for algo_name, algo_class in algorithms.items():
                print(f"  開始執行 {algo_name}...")

                # 選擇實體記憶體中的框架數量
                for num_frames in self.frame_sizes:
                    print("    Frame sizes: ", num_frames)
                    # 執行並將結果存到變數
                    algo = algo_class(num_frames)
                    faults, interrupts, writes = algo.run(ref_string)

                    # 記錄結果
                    self.results[ref_name][algo_name]["faults"].append(faults)
                    self.results[ref_name][algo_name]["interrupts"].append(interrupts)
                    self.results[ref_name][algo_name]["writes"].append(writes)

    def plot_results(self, algorithms):
        """
        繪製實驗結果圖表

        為每種置換演算法和每種參考字串提供三種圖表:
        1. Page Faults vs Frames
        2. Interrupts vs Frames
        3. Disk Writes vs Frames
        """
        print("\n開始畫圖")

        for ref_name in self.results:
            fig, axes = plt.subplots(1, 3, figsize=(15, 4))
            fig.suptitle(ref_name, fontsize=14)

            # 第一張圖:Page Faults
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

            # 第二張圖:Interrupts
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

            # 第三張圖:Disk Writes
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

            plt.tight_layout()
            filename = f'{ref_name.replace(" ", "_")}.png'
            plt.savefig(filename)
            print(f"  存檔: {filename}")

        plt.show()

    def print_summary(self, algorithms):
        """印出實驗結果摘要"""
        print("\n=== 實驗結果摘要 ===")

        for ref_name in self.results:
            print(f"\n{ref_name}:")

            for algo_name in algorithms:
                # 計算平均值
                avg_faults = sum(self.results[ref_name][algo_name]["faults"]) / len(
                    self.frame_sizes
                )
                avg_interrupts = sum(
                    self.results[ref_name][algo_name]["interrupts"]
                ) / len(self.frame_sizes)
                avg_writes = sum(self.results[ref_name][algo_name]["writes"]) / len(
                    self.frame_sizes
                )

                print(f"  {algo_name}:")
                print(f"    平均 Page Faults: {avg_faults:.0f}")
                print(f"    平均 Interrupts: {avg_interrupts:.0f}")
                print(f"    平均 Disk Writes: {avg_writes:.0f}")
