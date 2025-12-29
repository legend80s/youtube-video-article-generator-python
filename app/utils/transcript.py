import uuid
import hashlib

__all__ = ["QuickFragmentCheck"]

url = "http://www.youtube.com/watch?v=4KdvcQKNfbQ 水电费水电费"
hashed = hashlib.sha256(url.encode()).hexdigest()

print(f"{url} -> {hashed} → {len(hashed)}")
uuid_result = uuid.uuid5(uuid.NAMESPACE_DNS, url)

print(f"{url} -> {uuid_result} → {len(str(uuid_result))}")


words = url.split()[:3]  # 取前3个词

print(words)


def check_transcript_fragments(new_text: str, existing_text: str) -> bool:
    """
    检查新文本是否是已有文本的片段组合
    适用于：首段、中段、末段的任意组合
    """
    # 确保 existing_text 是较长的
    if len(new_text) > len(existing_text):
        new_text, existing_text = existing_text, new_text

    # 1. 完全包含
    if new_text in existing_text:
        return True

    # 2. 快速检查：查找至少2个50字符以上的连续片段
    fragment_count = 0
    i = 0

    while i < len(new_text) - 50:  # 需要至少50字符才能成为片段
        # 尝试从i开始找最长匹配
        max_len = 0
        for length in [100, 80, 60, 50]:  # 从长到短尝试
            if i + length <= len(new_text):
                if new_text[i : i + length] in existing_text:
                    max_len = length
                    break

        if max_len >= 50:
            fragment_count += 1
            i += max_len
            if fragment_count >= 2:
                return True  # 找到2个片段就够了
        else:
            i += 1  # 没找到，前进1字符

    return False


# 测试 first_part
# print("测试用例1（首段）:", check_transcript_fragments(first_part, long))
# # 测试 middle_part
# print("测试用例2（中段）:", check_transcript_fragments(middle_part, long))
# # 测试 last_part
# print("测试用例3（末段）:", check_transcript_fragments(last_part, long))


# print("测试用例1（三段组合1）:", check_transcript_fragments(short1, long))
# print("测试用例1（三段组合2）:", check_transcript_fragments(short11, long))
# print("测试用例2（first + middle）:", check_transcript_fragments(short2, long))
# print("测试用例3（first + last）:", check_transcript_fragments(short3, long))
# print("测试用例4（middle + last）:", check_transcript_fragments(short4, long))
# print("测试用例5（不相关内容）:", check_transcript_fragments(short5, long))


class QuickFragmentCheck:
    def __init__(
        self,
        sample_length_ratio: float = 0.2,
        min_sample_length: int = 30,
        max_sample_length: int = 150,
    ):
        self.sample_length_ratio = sample_length_ratio
        self.min_sample_length = min_sample_length
        self.max_sample_length = max_sample_length

    def is_similar(
        self,
        short_text: str,
        long_text: str,
        sample_length_ratio: None | float = None,
        min_sample_length: None | int = None,
        max_sample_length: None | int = None,
    ) -> bool:
        """
        极速检查：基于首尾特征快速判断
        假设片段组合通常会保留原文本的首尾特征
        """
        short = short_text.strip()
        long = long_text.strip()

        if len(short) > len(long):
            short, long = long, short

        # 1. 检查是否完全包含
        if short in long:
            return True

        # 2. 计算自适应采样长度
        if sample_length_ratio is None:
            sample_length_ratio = self.sample_length_ratio
        if min_sample_length is None:
            min_sample_length = self.min_sample_length
        if max_sample_length is None:
            max_sample_length = self.max_sample_length

        base_length = int(len(short) * sample_length_ratio)
        # 限制在[min_sample, max_sample]范围内
        sample_length = max(min_sample_length, min(base_length, max_sample_length))
        # print(f"short: {short}, len: {len(short)}")
        # print(f"long: {long}, len: {len(long)}")
        # print(f"sample_length_ratio: {sample_length_ratio}")
        # print(f"base_length: {base_length}")
        # print(f"min_sample_length: {min_sample_length}")
        # print(f"max_sample_length: {max_sample_length}")
        # print(f"sample_length: {sample_length}")

        # 3. 快速特征检查
        # 取短文本的前sample_length字符和后sample_length字符
        SAMPLE_LENGTH = sample_length
        front_sample = short[:SAMPLE_LENGTH] if len(short) > SAMPLE_LENGTH else short
        back_sample = short[-SAMPLE_LENGTH:] if len(short) > SAMPLE_LENGTH else short

        # 这两个特征是否都能在长文本中找到
        front_in_long = front_sample in long
        back_in_long = back_sample in long

        # print(f"front_sample: {front_sample}, len: {len(front_sample)}")
        # print(f"back_sample: {back_sample}, len: {len(back_sample)}")
        # print(f"front_in_long: {front_in_long}")
        # print(f"back_in_long: {back_in_long}")

        # 情况A：首尾都在长文本中 → 很可能是片段组合
        if front_in_long and back_in_long:
            return True

        # 情况B：只有一端在，检查中间是否有其他片段
        if front_in_long or back_in_long:
            # 尝试在中间找另一个片段
            middle_start = len(short) // 3
            middle_sample = short[middle_start : middle_start + SAMPLE_LENGTH]
            if middle_sample in long:
                return True

        return False

    # 让实例可调用：直接指向 is_similar 方法
    __call__ = is_similar


if __name__ == "__main__":
    long: str = "第一部分：介绍。第二部分：方法。第三部分：实验。第五部分：讨论。第六部分：结论。"
    # 首段
    first_part = "第一部分：介绍。"
    # 中段
    middle_part = "第三部分：实验。"
    # 末段
    last_part = "第六部分：结论。"

    short1 = "第一部分：介绍。第三部分：实验。第六部分：结论。"  # 三段组合1
    short11 = first_part + middle_part + last_part  # 三段组合2

    short2 = first_part + middle_part  # 两段组合
    # first + last
    short3 = first_part + last_part
    # middle + last
    short4 = middle_part + last_part

    short5 = "这是一个完全不同的内容。"  # 不相关内容

    is_similar = QuickFragmentCheck(min_sample_length=2)
    # print(f"\n{' is_similar ':#^60}")
    # 测试 first_part
    assert is_similar(first_part, long), "测试用例1（首段）应该返回 True"
    # 测试 middle_part
    assert is_similar(middle_part, long), "测试用例2（中段）应该返回 True"
    # 测试 last_part
    assert is_similar(last_part, long), "测试用例3（末段）应该返回 True"

    # 测试 short1
    assert is_similar(short1, long), "测试用例1（三段组合1）应该返回 True"
    # 测试 short11
    assert is_similar(short11, long), "测试用例1（三段组合2）应该返回 True"
    # 测试 short2
    assert is_similar(short2, long), "测试用例2（first + middle）应该返回 True"

    # 测试 short3
    assert is_similar(short3, long), "测试用例3（first + last）应该返回 True"

    # 测试 short4
    assert is_similar(short4, long), "测试用例4（middle + last）应该返回 True"
    # 测试 short5
    assert not is_similar(short5, long), "测试用例5（不相关内容）应该返回 False"

    print("\033[92m" + "所有测试用例通过！" + "\033[0m")
