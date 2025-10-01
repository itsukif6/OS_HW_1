# algorithms.py
"""
分頁置換演算法實作
包含 FIFO, Optimal, Additional-reference-bits, 自訂 (TwoZone)
"""


class PageReplacementAlgorithm:
    """分頁置換演算法的基礎類別"""

    def __init__(self, frames):
        """
        初始化演算法

        參數:
            frames: 可用的頁框數量
        """
        print("    初始化演算法")
        self.frames = frames
        self.faults = 0  # 分頁錯誤次數
        self.interrupts = 0  # 中斷次數
        self.writes = 0  # 磁碟寫入次數

    def run(self, ref_string):
        """
        執行演算法 (子類別需要實作)

        參數:
            ref_string: 參考字串
        回傳:
            (faults, interrupts, writes) 統計數據
        """
        raise NotImplementedError

    def reset(self):
        """重置統計數據"""
        print("    重置統計數據")
        self.faults = 0
        self.interrupts = 0
        self.writes = 0


class FIFO(PageReplacementAlgorithm):
    """FIFO algorithm"""

    def run(self, ref_string):
        self.reset()
        memory = []  # 目前在記憶體中的分頁
        queue = []  # FIFO佇列
        dirty = {}  # 記錄哪些分頁是髒的

        for page, is_write in ref_string:
            if page not in memory:
                # 分頁不在記憶體 -> Page Fault
                self.faults += 1
                self.interrupts += 1

                if len(memory) < self.frames:
                    # 還有空位, 直接放入
                    memory.append(page)
                    queue.append(page)
                else:
                    # 記憶體滿了, 踢掉最早進來的
                    victim = queue.pop(0)

                    # 如果被踢掉的分頁是髒的, 要寫回磁碟
                    if victim in dirty and dirty[victim]:
                        self.writes += 1

                    memory.remove(victim)
                    memory.append(page)
                    queue.append(page)

                    if victim in dirty:
                        del dirty[victim]

                dirty[page] = is_write
            else:
                # 分頁在記憶體中 -> Page Hit
                if is_write:
                    dirty[page] = True
        print(
            f"    Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes


class Optimal(PageReplacementAlgorithm):
    """Optimal algorithm"""

    def run(self, ref_string):
        self.reset()
        memory = []
        dirty = {}

        for i, (page, is_write) in enumerate(ref_string):
            if page not in memory:
                self.faults += 1
                self.interrupts += 1

                if len(memory) < self.frames:
                    memory.append(page)
                else:
                    # 找出未來最久才會用到的分頁
                    victim = self._find_victim(memory, ref_string, i)

                    if victim in dirty and dirty[victim]:
                        self.writes += 1

                    memory.remove(victim)
                    memory.append(page)

                    if victim in dirty:
                        del dirty[victim]

                dirty[page] = is_write
            else:
                if is_write:
                    dirty[page] = True
        print(
            f"    Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes

    def _find_victim(self, memory, ref_string, current):
        """
        找出最佳的犧牲者（未來最久才會用到的分頁)

        參數:
            memory: 目前記憶體中的分頁
            ref_string: 完整的參考字串
            current: 目前的位置
        """
        max_dist = -1
        victim = memory[0]

        for page in memory:
            # 找這個分頁下次會在什麼時候用到
            found = False
            for j in range(current + 1, len(ref_string)):
                # ref_string[j] 是 (page, is_write) tuple
                if ref_string[j][0] == page:
                    if j > max_dist:
                        max_dist = j
                        victim = page
                    found = True
                    break

            # 如果未來都不會用到, 就選這個
            if not found:
                return page

        return victim


class ReferenceBits(PageReplacementAlgorithm):
    """Additional-reference-bits algorithm"""

    def run(self, ref_string):
        self.reset()
        memory = []
        bits = {}  # 每個分頁的8-bit參考位元
        dirty = {}

        for i, (page, is_write) in enumerate(ref_string):
            # 定期將所有參考位元右移
            if i > 0 and i % 100 == 0:
                for p in memory:
                    bits[p] = bits[p] >> 1

            if page not in memory:
                self.faults += 1
                self.interrupts += 1

                if len(memory) < self.frames:
                    memory.append(page)
                    bits[page] = 128  # 0b10000000 最左邊設1
                else:
                    # 找參考位元值最小的（最少被用到)
                    victim = min(memory, key=lambda p: bits[p])

                    if victim in dirty and dirty[victim]:
                        self.writes += 1

                    memory.remove(victim)
                    memory.append(page)
                    del bits[victim]
                    bits[page] = 128

                    if victim in dirty:
                        del dirty[victim]

                dirty[page] = is_write
            else:
                # 分頁命中, 將最左邊的bit設為1
                bits[page] = bits[page] | 128
                if is_write:
                    dirty[page] = True
        print(
            f"    Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes


class ARC(PageReplacementAlgorithm):
    """Adaptive Replacement Cache (ARC)"""

    def run(self, ref_string):
        self.reset()

        # 四個集合
        T1, T2 = [], []  # 真正的快取頁面
        B1, B2 = [], []  # ghost lists (只存 page id)

        # dirty 紀錄
        dirty = {}
        self.p = 0  # 動態調整參數

        def replace(page):
            """選擇一個頁面淘汰"""
            if T1 and ((len(T1) > self.p) or (page in B2 and len(T1) == self.p)):
                victim = T1.pop(0)
                B1.append(victim)
                if victim in dirty and dirty[victim]:
                    self.writes += 1
                dirty.pop(victim, None)
            elif T2:
                victim = T2.pop(0)
                B2.append(victim)
                if victim in dirty and dirty[victim]:
                    self.writes += 1
                dirty.pop(victim, None)
            else:
                # 這個情況只會在初始化早期出現
                return

        for page, is_write in ref_string:
            # 命中在 T1 或 T2
            if page in T1 or page in T2:
                if page in T1:
                    T1.remove(page)
                    T2.append(page)  # 提升到 T2
                elif page in T2:
                    T2.remove(page)
                    T2.append(page)  # 更新 recency
                if is_write:
                    dirty[page] = True
                continue

            # 命中在 B1
            if page in B1:
                self.p = min(self.p + max(1, len(B2) // max(1, len(B1))), self.frames)
                replace(page)
                B1.remove(page)
                T2.append(page)
                if is_write:
                    dirty[page] = True
                self.faults += 1
                self.interrupts += 1
                continue

            # 命中在 B2
            if page in B2:
                self.p = max(self.p - max(1, len(B1) // max(1, len(B2))), 0)
                replace(page)
                B2.remove(page)
                T2.append(page)
                if is_write:
                    dirty[page] = True
                self.faults += 1
                self.interrupts += 1
                continue

            # 完全不在 (Page Fault)
            self.faults += 1
            self.interrupts += 1

            if len(T1) + len(T2) == self.frames:
                replace(page)

            if len(T1) + len(T2) < self.frames:
                T1.append(page)
            else:
                # 若 frame 已滿，由 replace() 決定
                T1.append(page)

            if is_write:
                dirty[page] = True

        print(
            f"      Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes
