"""
智能匹配算法
"""
import json


def calculate_interest_match(student_scores, club_tags):
    """
    计算兴趣契合度
    :param student_scores: 学生的兴趣分数 {"arts": 80, "sports": 60, ...}
    :param club_tags: 社团标签列表 ["文艺", "音乐"]
    :return: 契合度分数 0-100
    """
    if not student_scores or not club_tags:
        return 50  # 默认中等分数

    # 标签到兴趣维度的映射
    tag_to_dimension = {
        "文艺": "arts", "音乐": "arts", "舞蹈": "arts", "话剧": "arts", "摄影": "arts",
        "体育": "sports", "篮球": "sports", "足球": "sports", "羽毛球": "sports", "跑步": "sports",
        "学术": "academic", "科研": "academic", "辩论": "academic", "英语": "academic",
        "公益": "charity", "志愿者": "charity", "环保": "charity",
        "技术": "tech", "编程": "tech", "机器人": "tech", "计算机": "tech", "创业": "tech"
    }

    # 计算社团标签对应维度的平均分
    relevant_scores = []
    for tag in club_tags:
        dimension = tag_to_dimension.get(tag)
        if dimension and dimension in student_scores:
            relevant_scores.append(student_scores[dimension])

    if relevant_scores:
        return sum(relevant_scores) / len(relevant_scores)
    return 50


def calculate_time_match(student_time, club_time):
    """
    计算时间匹配度
    :param student_time: 学生可用时间 {"mon": ["evening"], ...}
    :param club_time: 社团活动时间 {"mon": ["evening"], ...}
    :return: 匹配度分数 0-100
    """
    if not student_time or not club_time:
        return 70  # 默认较高分数

    student_slots = set()
    club_slots = set()

    for day, times in student_time.items():
        for t in times:
            student_slots.add(f"{day}_{t}")

    for day, times in club_time.items():
        for t in times:
            club_slots.add(f"{day}_{t}")

    if not club_slots:
        return 70

    # 计算交集比例
    overlap = len(student_slots & club_slots)
    return min(100, overlap * 20 + 40)  # 每个重叠时间段加20分


def calculate_major_match(student_major, club_requirements):
    """
    计算专业相关性
    :param student_major: 学生专业
    :param club_requirements: 社团要求
    :return: 匹配度分数 0-100
    """
    if not club_requirements:
        return 70

    # 某些社团对特定专业有偏好
    major_preferences = {
        "计算机": ["技术", "编程", "机器人"],
        "软件": ["技术", "编程"],
        "电子": ["技术", "机器人"],
        "音乐": ["文艺", "音乐"],
        "体育": ["体育"],
        "外语": ["学术", "英语"],
    }

    preferred_tags = major_preferences.get(student_major, [])

    if any(tag in club_requirements for tag in preferred_tags):
        return 90

    return 70


def calculate_personality_match(student_scores, club_category):
    """
    计算性格适配度（简化版）
    :param student_scores: 兴趣分数
    :param club_category: 社团类别
    :return: 适配度分数 0-100
    """
    # 性格倾向与社团类别的匹配
    personality_match = {
        "arts": ["文艺", "音乐", "舞蹈", "话剧"],
        "sports": ["体育", "篮球", "足球"],
        "academic": ["学术", "科研", "辩论"],
        "charity": ["公益", "志愿者"],
        "tech": ["技术", "编程", "机器人"]
    }

    if not club_category:
        return 70

    # 找出学生最高分的维度
    if student_scores:
        top_dimension = max(student_scores.items(), key=lambda x: x[1])[0]
        if club_category in personality_match.get(top_dimension, []):
            return 90

    return 70


def calculate_match_score(student, club):
    """
    计算综合匹配分数
    :param student: 学生对象
    :param club: 社团对象
    :return: 匹配分数和匹配理由
    """
    # 解析学生数据
    student_scores = json.loads(student.interest_scores) if student.interest_scores else {}
    student_time = json.loads(student.time_available) if student.time_available else {}

    # 解析社团数据
    club_tags = club.tags.split(',') if club.tags else []
    club_time = json.loads(club.activity_time) if club.activity_time else {}

    # 计算各维度分数
    interest_score = calculate_interest_match(student_scores, club_tags)
    time_score = calculate_time_match(student_time, club_time)
    major_score = calculate_major_match(student.major, club.requirements or "")
    personality_score = calculate_personality_match(student_scores, club.category)

    # 加权计算总分
    total_score = (
        interest_score * 0.4 +
        time_score * 0.25 +
        major_score * 0.2 +
        personality_score * 0.15
    )

    # 生成匹配理由
    reasons = []
    if interest_score >= 70:
        reasons.append(f"兴趣契合度高({interest_score:.0f}分)")
    if time_score >= 70:
        reasons.append("时间安排匹配")
    if major_score >= 80:
        reasons.append("专业背景相关")
    if personality_score >= 80:
        reasons.append("性格特点适合")

    if not reasons:
        reasons.append("综合评估推荐")

    return round(total_score, 1), reasons


def get_recommendations(student, clubs, top_n=5):
    """
    获取推荐社团列表
    :param student: 学生对象
    :param clubs: 社团列表
    :param top_n: 返回前N个推荐
    :return: 排序后的推荐列表 [(club, score, reasons), ...]
    """
    recommendations = []

    for club in clubs:
        if club.is_recruiting:
            score, reasons = calculate_match_score(student, club)
            recommendations.append((club, score, reasons))

    # 按分数降序排序
    recommendations.sort(key=lambda x: x[1], reverse=True)

    return recommendations[:top_n]


def generate_student_tags(interest_scores):
    """
    根据兴趣分数生成学生标签
    :param interest_scores: {"arts": 80, "sports": 60, ...}
    :return: 标签列表
    """
    if not interest_scores:
        return ["综合型"]

    tag_mapping = {
        "arts": "文艺青年",
        "sports": "运动达人",
        "academic": "学术探索",
        "charity": "公益热心",
        "tech": "技术控"
    }

    tags = []
    for dimension, score in interest_scores.items():
        if score >= 70:
            tags.append(tag_mapping.get(dimension, ""))

    if not tags:
        tags = ["综合型"]

    return tags
