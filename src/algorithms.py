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
        self.reset()  # 重置所有數據
        memory = []  # 目前在記憶體中的分頁
        queue = []  # FIFO 佇列
        dirty = {}  # 記錄哪些分頁是髒的

        for page, is_write in ref_string:
            if page not in memory:
                # 分頁不在記憶體 => Page Fault
                self.faults += 1
                self.interrupts += 1

                # 記憶體不夠, 直接加
                if len(memory) < self.frames:
                    memory.append(page)
                    queue.append(page)

                # 記憶體不夠
                else:
                    # 踢掉最早進來的
                    victim = queue.pop(0)

                    # 如果被踢掉的分頁是髒的, 要寫回磁碟
                    if victim in dirty and dirty[victim]:
                        self.writes += 1
                        self.interrupts += 1

                    # 刪除舊的 victim page, 加入新的 page 到 memory 跟 FIFO 序列中
                    memory.remove(victim)
                    memory.append(page)
                    queue.append(page)

                    # 如果被踢掉的分頁是髒的, 要刪除 dirty list 中的 page
                    if victim in dirty:
                        del dirty[victim]

                # 將 dirty list 中的 key 對應的 value 改為 is_write 的值
                dirty[page] = is_write

            else:
                # 分頁在記憶體中 => Page Hit
                # 若 is_write, 將 dirty list 中的 key 對應的 value 改為 True
                if is_write:
                    dirty[page] = True
        print(
            f"    Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes


class Optimal(PageReplacementAlgorithm):
    """Optimal algorithm (預先計算未來出現位置)"""

    def run(self, ref_string):
        self.reset()  # 重置所有數據
        memory = []  # 目前在記憶體中的分頁
        dirty = {}  # 記錄哪些分頁是髒的

        # 預先建立 future_positions: 每個 page 的出現索引列表
        future_positions = {}

        # loop 整個參考字串並建立 future_positions, _ 代表忽略 is_write
        for i, (page, _) in enumerate(ref_string):

            # 如果這個 page 第一次出現在字典中, 先建立一個空列表
            if page not in future_positions:
                future_positions[page] = []

            # 將這次出現的位置 i 加入到該 page 的列表中
            future_positions[page].append(i)

        for i, (page, is_write) in enumerate(ref_string):
            # 移除這次出現的 page 在 future_positions 中的位置
            future_positions[page].pop(0)

            if page not in memory:
                # 分頁不在記憶體 => Page Fault
                self.faults += 1
                self.interrupts += 1

                # 記憶體還夠, 直接加
                if len(memory) < self.frames:
                    memory.append(page)

                # 記憶體不夠
                else:
                    # 先找出未來最久才會用到的分頁
                    victim = self._find_victim(memory, future_positions)

                    # 如果被踢掉的分頁是髒的, 要寫回磁碟
                    if victim in dirty and dirty[victim]:
                        self.writes += 1
                        self.interrupts += 1

                    # 刪除舊的 victim page, 加入新的 page 到 memory 中
                    memory.remove(victim)
                    memory.append(page)

                    # 如果被踢掉的分頁是髒的, 要刪除 dirty list 中的 page
                    if victim in dirty:
                        del dirty[victim]

                # 將 dirty list 中的 key 對應的 value 改為 is_write 的值
                dirty[page] = is_write
            else:
                # 分頁在記憶體中 => Page Hit
                # 若 is_write, 將 dirty list 中的 key 對應的 value 改為 True
                if is_write:
                    dirty[page] = True

        print(
            f"    Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes

    def _find_victim(self, memory, future_positions):
        """找犧牲者"""
        max_dist = -1  # 初始化最大距離為 -1, 用來追蹤未來最遠才會用到的位置
        victim = memory[0]  # 預設犧牲者為記憶體中的第一個 page

        # loop 記憶體中的每個 page, 找出最適合被踢掉的
        for page in memory:

            # 檢查這個 page 未來還會不會被用到
            if future_positions[page]:  # 如果列表不是空的, 表示未來還會出現

                # 取得下次出現的位置
                next_use = future_positions[page][0]

            else:  # 如果列表是空的, 表示未來不會再被用到, 直接回傳
                return page

            # 如果這個 page 的下次出現位置比目前記錄的最大距離還遠
            if next_use > max_dist:
                max_dist = next_use  # 更新最大距離
                victim = page  # 更新犧牲者為這個 page

        # 回傳找到的犧牲者
        return victim


class ReferenceBits(PageReplacementAlgorithm):
    """Additional-reference-bits algorithm"""

    def run(self, ref_string):
        self.reset()  # 重置所有數據
        memory = []  # 目前在記憶體中的分頁
        bits = {}  # 儲存每個分頁的 8-bit 參考位元 (0~255)
        dirty = {}  # 記錄哪些分頁是髒的

        for i, (page, is_write) in enumerate(ref_string):
            # 定期將所有參考位元右移 (每 100 次 loop)
            if i > 0 and i % 100 == 0:
                for p in memory:
                    bits[p] = bits[p] >> 1  # 將該 page 的 8-bit 右移一位 (除以 2)

            # 分頁不在記憶體 => Page Fault
            if page not in memory:
                self.faults += 1
                self.interrupts += 1

                # 記憶體還夠, 直接加
                if len(memory) < self.frames:
                    memory.append(page)
                    bits[page] = 128  # 0b10000000 => 最左邊設1

                # 記憶體不夠, 找犧牲者
                else:
                    # 找參考位元值最小的 = 最少用到 (找 memory 每一個數對應的 bits[p] 最小的)
                    victim = min(memory, key=lambda p: bits[p])

                    # 如果被踢掉的分頁是髒的, 要寫回磁碟
                    if victim in dirty and dirty[victim]:
                        self.writes += 1
                        self.interrupts += 1

                    # 從記憶體中移除 victim，並加上新的 page
                    memory.remove(victim)
                    memory.append(page)
                    del bits[victim]
                    bits[page] = 128  # 0b10000000 => 最左邊設1

                    # 如果被踢掉的分頁是髒的, 要刪除 dirty list 中的 page
                    if victim in dirty:
                        del dirty[victim]

                # 將 dirty list 中的 key 對應的 value 改為 is_write 的值
                dirty[page] = is_write
            else:
                # 分頁命中, 將最左邊的bit設為1 (0b10000000)
                bits[page] = bits[page] | 128
                # 若 is_write, 將 dirty list 中的 key 對應的 value 改為 True
                if is_write:
                    dirty[page] = True
        print(
            f"    Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes


class ARC(PageReplacementAlgorithm):
    """
    Adaptive Replacement Cache (ARC)
    方法參考: https://www.usenix.org/legacy/events/fast03/tech/full_papers/megiddo/megiddo.pdf

    T1:             list, 儲存「只被用過一次」且目前在 cache 的頁面。
    T2:             list, 儲存「被多次存取」且在 cache 的頁面。
    B1:             list, ghost list, 只記錄從 T1 驅逐出去的 page id (不占 frame)。
    B2:             list, ghost list, 只記錄從 T2 驅逐出去的 page id。
    dirty:          dict, page => bool, 標示該頁面是否為髒 (需要寫回)。
    self.p:         整數, ARC 的自適應參數, 用來調整 T1 與 T2 的相對大小 (範圍被限制在 [0, frames])。
    replace(page):  負責根據 p 與 ghost hits 決定要從 T1 還是 T2 淘汰一個頁面, 並把被淘汰者放到對應的 ghost list (B1 或 B2)。
    """

    def run(self, ref_string):
        self.reset()

        # 四個 lists
        T1, T2 = [], []  # 真正的快取頁面
        B1, B2 = [], []  # ghost lists (只存 page id)

        # dirty 紀錄
        dirty = {}
        self.p = 0  # 動態調整參數, p = 0 表示初期偏向 T2 (T2 較重要)

        def replace(page):
            """
            選擇一個頁面淘汰
            條件: T1 非空 且 (|T1| > p 或 (page 在 B2 且 |T1| == p))
            """
            # 當 T1 非空 且 (|T1| > p 或 (page 在 B2 且 |T1| == p))
            if T1 and ((len(T1) > self.p) or (page in B2 and len(T1) == self.p)):
                victim = T1.pop(0)
                B1.append(victim)  # 移到 ghost list 最後

                # 如果是 dirty page, 需要寫回
                if victim in dirty and dirty[victim]:
                    self.writes += 1
                    self.interrupts += 1

                # 清除 dirty 狀態 (使用 pop 避免 KeyError)
                dirty.pop(victim, None)

            elif T2:
                victim = T2.pop(0)
                B2.append(victim)  # 移到 ghost list 最後

                # 如果是 dirty page, 需要寫回
                if victim in dirty and dirty[victim]:
                    self.writes += 1
                    self.interrupts += 1

                # 清除 dirty 狀態 (使用 pop 避免 KeyError)
                dirty.pop(victim, None)

            else:
                # 這種情況理論上不應該發生 (T1 和 T2 都空了但還要 replace)
                return

        for page, is_write in ref_string:
            # Case 1: 命中在 T1 或 T2, 表示命中的 page 經常被使用
            if page in T1 or page in T2:

                # Hit, 不計數 fault 和 interrupt
                if page in T1:
                    T1.remove(page)
                    T2.append(page)  # 提升到 T2 (因為被訪問第二次了)

                elif page in T2:
                    T2.remove(page)
                    T2.append(page)  # 更新 T2 (最新的移到最後)

                # 更新 dirty bit
                if is_write:
                    dirty[page] = True

                continue

            # Case 2: 命中在 B1, 表示 page 只被使用一次就 pop 掉了, 所以調整 p 的大小 (增加 p)
            if page in B1:
                # 調整 p: 增加 T1 的目標大小 (因為 B1 hit 表示應該保留更多「只訪問一次」的頁面)
                self.p = min(self.p + max(1, len(B2) // max(1, len(B1))), self.frames)

                # 選一個 victim 來 replace
                replace(page)

                # 從 B1 移除並加入 T2 (因為現在是第二次訪問了)
                B1.remove(page)
                T2.append(page)

                # 設置 dirty bit (因為是新載入的頁面)
                if is_write:
                    dirty[page] = True

                # Case 2 是 Page Fault (頁面不在 memory 中)
                self.faults += 1
                self.interrupts += 1
                continue

            # Case 3: 命中在 B2, 表示 page 曾經被多次使用, 但還是被 pop, 所以要調整 p 的大小 (減少 p)
            if page in B2:
                # 調整 p: 減少 T1 的目標大小 (因為 B2 命中表示應該保留更多「訪問一次以上」的頁面)
                self.p = max(self.p - max(1, len(B1) // max(1, len(B2))), 0)

                # 選一個 victim 來 replace
                replace(page)

                # 從 B2 移除並加入 T2
                B2.remove(page)
                T2.append(page)

                # 設置 dirty bit (因為是新載入的頁面)
                if is_write:
                    dirty[page] = True

                # Case 3 是 Page Fault (頁面不在 memory 中)
                self.faults += 1
                self.interrupts += 1

                continue

            # Case 4: 不在 T1, T2, B1, B2 中 (Page Fault)
            self.faults += 1
            self.interrupts += 1

            # Case 4-A: |T1| + |B1| = c (frames)
            # 當 T1 和 B1 的總大小已達到 frames 的大小, 但 T2 和 B2 還有空間（因為總共可以有 2c 個頁面的大小可以使用）, 表示此時正在大量使用「只訪問一次」的頁面
            if len(T1) + len(B1) == self.frames:
                if len(T1) < self.frames:
                    # 如果 T1 沒滿, 表示有太多使用一下子就被 pop 掉的頁面 => 從 B1 刪除 LRU 頁面, 並用 replace 騰出實際的空間
                    B1.pop(0)
                    # 只有當 T1+T2 已滿時才需要 replace
                    if len(T1) + len(T2) >= self.frames:
                        replace(page)
                else:
                    # if |T1| = c, 表示 T1 滿了, B1 是空的 => 不需要執行 Replace, 直接從 T1 刪除 LRU 並添加到 B1
                    removed = T1.pop(0)
                    # 如果被移除的頁面是 dirty, 需要寫回
                    if removed in dirty and dirty[removed]:
                        self.writes += 1
                        self.interrupts += 1
                    # 清除 dirty 狀態 (使用 pop 避免 KeyError)
                    dirty.pop(removed, None)
                    B1.append(removed)

            # Case 4-B: |T1| + |B1| < c (frames)
            # T1 + B1 的總和還沒達到 c (frames), 但 |T1| + |T2| + |B1| + |B2| 可能已經達到 2c (2frames)
            else:
                total_size = len(T1) + len(T2) + len(B1) + len(B2)
                if total_size >= 2 * self.frames:
                    # 若|T1| + |T2| + |B1| + |B2| 已經達到 2c, 需要從 ghost list 中刪除一個 frame 以騰出空間
                    if B2:
                        # B1 還有空間，但 B2 已經太大了，所以從 B2 刪除 LRU 頁面
                        B2.pop(0)

                # 只有當 T1 + T2 已滿時才需要 replace
                if len(T1) + len(T2) >= self.frames:
                    replace(page)

            # 最後將新頁面加入 T1 (因為是第一次訪問)
            T1.append(page)

            # 維護 dirty bit (新頁面根據是否是寫操作來設置)
            if is_write:
                dirty[page] = True

        print(
            f"    Faults: {self.faults}, Interrupts: {self.interrupts}, Writes: {self.writes}"
        )
        return self.faults, self.interrupts, self.writes
