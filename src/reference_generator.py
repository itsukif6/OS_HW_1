# reference_generator.py
import random


class ReferenceGenerator:
    """參考字串產生器 (Reference String Generator)

    用於模擬作業系統記憶體或快取的「頁面存取序列」，
    可產生不同型態的測試資料:
    - 隨機型 (Random): 完全隨機訪問。
    - 區域性型 (Locality): 模擬真實應用中區域性原則。
    - Zipf: 自己選擇的字串生成方式。
    """

    def __init__(self, length=300000, page_range=(1, 1500)):
        """
        初始化，設定參考字串長度與頁面範圍。

        參數:
            length: 參考字串長度 (預設 300,000 次)
            page_range: 分頁編號範圍 (預設 1~1500)
        """
        self.length = length
        self.min_page, self.max_page = page_range

    def generate_random(self):
        """
        產生完全隨機的頁面訪問序列，每次訪問都在所有頁面範圍中均勻隨機挑選。

        讀寫比例:
        - 讀取約 70%
        - 寫入約 30%

        選擇此比例的原因：一般經驗法則
        (選擇此比例的來源: https://www.dell.com/support/kbdoc/en-us/000299003/live-optics-basics-read-write-ratio)

        回傳:
            list[tuple[int, bool]] -> [(page, is_write), ...]
            其中 is_write 為 True 代表寫入，False 代表讀取。
        """
        result = []
        for _ in range(self.length):
            # 在頁面範圍內隨機挑一頁
            page = random.randint(self.min_page, self.max_page)

            # 隨機決定是否為寫入操作 (30% 機率)
            is_write = random.random() < 0.3

            result.append((page, is_write))

        print("Random 生成完畢")
        return result

    def generate_locality(self):
        """
        有區域性的參考字串。

        讀寫比例:
        - 讀取 70%
        - 寫入 30%
        (選擇此比例的來源: https://www.dell.com/support/kbdoc/en-us/000299003/live-optics-basics-read-write-ratio)

        回傳:
            [(page, is_write), ...]
        """
        result = []

        # 不斷生成，直到達到指定長度
        while len(result) < self.length:
            # 隨機挑選一個區域起始點
            # 為避免超出範圍，確保起始點 + 40 <= max_page
            start = random.randint(self.min_page, self.max_page - 40)

            # local_pages 包含 40 個連續 page
            local_pages = list(range(start, start + 40))

            # 在 local_pages 中執行多次存取
            for _ in range(1000):
                if len(result) >= self.length:
                    break

                # 從當前區域中挑一頁
                page = random.choice(local_pages)

                # 讀寫比例: 讀取 70%, 寫入 30%
                is_write = random.random() < 0.3

                # 加入結果清單
                result.append((page, is_write))
        print("Locality 生成完畢")
        return result

    def generate_zipf(self, alpha=1.2):
        """
        Zipf 分布的參考字串。

        依據:
        - Zipf 分布表示存取第 n 個記錄的機率與 1/n^s 成正比，s 為偏斜參數。
        - 實際測試顯示 80-90% 的存取集中在 10-20% 的頁面。
        - 大多數頁面很少被存取。

        讀寫比例:
        - 讀取 70%
        - 寫入 30%
        (選擇此比例的來源: https://www.dell.com/support/kbdoc/en-us/000299003/live-optics-basics-read-write-ratio)

        參數:
            alpha: Zipf 參數 (1.0-1.5 為典型值)

        回傳:
            [(page, is_write), ...]
        """
        import numpy as np

        # 使用 Zipf 分布產生頁面編號，alpha 就是公式中的偏斜參數（s 值）。
        pages = np.random.zipf(alpha, self.length)
        # 將頁面映射到有效範圍，因為 np.random.zipf() 會產生理論上無上限的整數。
        pages = ((pages - 1) % (self.max_page - self.min_page + 1)) + self.min_page

        result = []

        # 對每一頁隨機決定是否為寫入，讀寫比例: 讀取 70%, 寫入 30%
        for page in pages:
            is_write = random.random() < 0.3
            result.append((int(page), is_write))

        print("Zipf 生成完畢")
        return result
