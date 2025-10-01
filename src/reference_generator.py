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

    def generate_mixed(self):
        """
        我選擇的測試用參考字串: 混合型 (70%區域性 + 30%隨機)

        原因: 更接近真實程式的行為
        - 大部分時間在特定區域執行
        - 偶爾會跳到其他地方 (如: 呼叫其他函式、存取全域變數)

        讀寫模式:
        - 區域性存取:較多寫入 (30+10=40%), 因為可能在修改區域變數
        - 隨機跳躍:較多讀取 (70+10=80%), 因為可能在讀取資料結構 or 套件 (寫入=30-10=20%)
        """
        result = []

        while len(result) < self.length:
            if random.random() < 0.7:
                # 70%機率:區域性存取，並假設連續頁面區段大小 = 60
                start = random.randint(self.min_page, self.max_page - 60) 
                local_pages = list(range(start, start + 60))
                burst_length = random.randint(50, 200)

                for _ in range(burst_length):
                    if len(result) >= self.length:
                        break
                    page = random.choice(local_pages)
                    is_write = random.random() < 0.4  # 區域內較多寫入
                    result.append((page, is_write))
            else:
                # 30%機率:隨機跳躍
                page = random.randint(self.min_page, self.max_page)
                is_write = random.random() < 0.2  # 跳躍時多半是讀取
                result.append((page, is_write))
        print("Mixed 生成完畢")
        return result
