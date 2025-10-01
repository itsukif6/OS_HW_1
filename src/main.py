# main.py
"""
主程式
整合所有模組並執行實驗
"""


from algorithms import FIFO, Optimal, ReferenceBits, ARC
from reference_generator import ReferenceGenerator
from simulator import Simulator


def main():
    print("分頁置換演算法模擬器")
    print("=" * 50)

    # 產生參考字串
    print("\n生成參考字串...")
    generator = ReferenceGenerator()

    references = {
        "Random": generator.generate_random(),
        "Locality": generator.generate_locality(),
        "Mixed": generator.generate_mixed(),
    }

    # 定義要測試的演算法
    algorithms = {
        "FIFO": FIFO,
        # "Optimal": Optimal,
        "ReferenceBits": ReferenceBits,
        "ARC": ARC,
    }

    # 執行模擬
    simulator = Simulator()
    print("執行模擬")
    simulator.run_experiments(references, algorithms)

    # 繪製圖表
    print("繪製圖表")
    simulator.plot_results(algorithms)

    # 印出摘要
    print("印出摘要")
    simulator.print_summary(algorithms)

    print("\n完成")


if __name__ == "__main__":
    main()
