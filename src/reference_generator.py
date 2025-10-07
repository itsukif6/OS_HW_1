# reference_generator.py
"""
參考字串產生器
產生三種不同特性的參考字串用於測試
"""
import random


class ReferenceGenerator:
    """參考字串產生器"""

    def __init__(self, length=300000, page_range=(1, 1500)):
        """
        初始化產生器

        參數:
            length: 參考字串長度
            page_range: 分頁編號範圍
        """
        self.length = length
        self.min_page, self.max_page = page_range

    def generate_random(self):
        """
        隨機的參考字串

        讀寫比例:
        - 讀取 70%
        - 寫入 30%
        (選擇此比例的來源: https://www.dell.com/support/kbdoc/en-us/000299003/live-optics-basics-read-write-ratio)

        回傳:[(page, is_write), ...]
        """
        result = []
        for _ in range(self.length):
            page = random.randint(self.min_page, self.max_page)
            is_write = random.random() < 0.3  # 假設有 30% 機率是寫入
            result.append((page, is_write))
        print("Random 生成完畢")
        return result

    def generate_locality(self):
        """
        有區域性的參考字串

        讀寫比例:
        - 讀取 70%
        - 寫入 30%
        (選擇此比例的來源: https://www.dell.com/support/kbdoc/en-us/000299003/live-optics-basics-read-write-ratio)

        回傳:[(page, is_write), ...]
        """
        result = []

        while len(result) < self.length:
            # 隨機選一個區域的起點，並假設連續頁面區段大小 = 40
            start = random.randint(self.min_page, self.max_page - 40)
            local_pages = list(range(start, start + 40))

            # 在這個區域內產生1000次參考
            for _ in range(1000):
                if len(result) >= self.length:
                    break
                page = random.choice(local_pages)
                is_write = random.random() < 0.3
                result.append((page, is_write))
        print("Locality 生成完畢")
        return result

    def generate_zipf(self, alpha=1.2):
        """
        Zipf 分布的參考字串

        依據:
        - "Characterizing Application Memory Access Patterns" (Intel, 2010)
        - 實際測試顯示 80-90% 的存取集中在 10-20% 的頁面

        參數:
            alpha: Zipf 參數 (1.0-1.5 為典型值)
        """
        import numpy as np

        # 使用 Zipf 分布產生頁面編號
        pages = np.random.zipf(alpha, self.length)
        # 將頁面映射到有效範圍
        pages = (pages % (self.max_page - self.min_page + 1)) + self.min_page

        result = []
        for page in pages:
            is_write = random.random() < 0.3
            result.append((int(page), is_write))

        print("Zipf 生成完畢")
        return result
