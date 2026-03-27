"""
初始化测试数据
"""
from app import app
from models import db, Student, Club, Application
import json

def init_test_data():
    with app.app_context():
        # 创建数据库表
        db.create_all()

        # 检查是否已有数据
        if Club.query.first():
            print("数据库已有数据，跳过初始化")
            return

        # 创建测试社团
        clubs_data = [
            {
                "name": "吉他社",
                "category": "文艺",
                "description": "专注于吉他演奏技巧的学习与交流，定期举办音乐会和教学活动，欢迎所有对吉他感兴趣的同学加入！",
                "requirements": "热爱音乐，有学习热情即可",
                "tags": "文艺,音乐,吉他",
                "activity_time": json.dumps({"wed": ["evening"], "sat": ["afternoon"]}),
                "contact": "张学长",
                "admin_password": "123456"
            },
            {
                "name": "篮球俱乐部",
                "category": "体育",
                "description": "篮球爱好者的天堂！我们组织校内外比赛、训练活动，提升球技，结交朋友。",
                "requirements": "热爱篮球，愿意参与团队训练",
                "tags": "体育,篮球,运动",
                "activity_time": json.dumps({"tue": ["afternoon"], "thu": ["afternoon"], "sat": ["morning"]}),
                "contact": "李队长",
                "admin_password": "123456"
            },
            {
                "name": "编程协会",
                "category": "技术",
                "description": "学习编程技术，参与项目实战，举办技术分享会。无论你是小白还是大神，都能在这里找到成长的机会。",
                "requirements": "对编程有兴趣，有学习热情",
                "tags": "技术,编程,计算机,创业",
                "activity_time": json.dumps({"mon": ["evening"], "fri": ["evening"]}),
                "contact": "王会长",
                "admin_password": "123456"
            },
            {
                "name": "青年志愿者协会",
                "category": "公益",
                "description": "参与社会公益活动，服务社区，传递爱心。我们组织支教、环保、助老等各类志愿活动。",
                "requirements": "有爱心，愿意参与志愿服务",
                "tags": "公益,志愿者,环保",
                "activity_time": json.dumps({"sat": ["morning", "afternoon"], "sun": ["afternoon"]}),
                "contact": "陈学姐",
                "admin_password": "123456"
            },
            {
                "name": "辩论队",
                "category": "学术",
                "description": "锻炼口才与逻辑思维，参与校内外辩论赛事。每周组织讨论和模拟辩论。",
                "requirements": "对辩论有兴趣，愿意投入训练时间",
                "tags": "学术,辩论,演讲",
                "activity_time": json.dumps({"wed": ["evening"], "sun": ["afternoon"]}),
                "contact": "刘队长",
                "admin_password": "123456"
            },
            {
                "name": "摄影协会",
                "category": "文艺",
                "description": "记录生活美好瞬间，学习摄影技巧。定期组织外拍活动和摄影展览。",
                "requirements": "对摄影有兴趣，有相机或手机即可",
                "tags": "文艺,摄影,艺术",
                "activity_time": json.dumps({"sat": ["afternoon"]}),
                "contact": "周学长",
                "admin_password": "123456"
            },
            {
                "name": "机器人创新实验室",
                "category": "技术",
                "description": "探索机器人技术，参与创新竞赛。涵盖机械设计、电子电路、编程控制等领域。",
                "requirements": "对机器人有兴趣，愿意学习新技术",
                "tags": "技术,机器人,创新",
                "activity_time": json.dumps({"tue": ["evening"], "thu": ["evening"], "sat": ["afternoon"]}),
                "contact": "赵老师",
                "admin_password": "123456"
            },
            {
                "name": "英语角",
                "category": "学术",
                "description": "提升英语口语能力，了解西方文化。每周组织英语角活动、英语电影欣赏等。",
                "requirements": "想提高英语口语的同学",
                "tags": "学术,英语,语言",
                "activity_time": json.dumps({"fri": ["evening"]}),
                "contact": "Sarah",
                "admin_password": "123456"
            }
        ]

        for data in clubs_data:
            club = Club(**data)
            db.session.add(club)

        db.session.commit()
        print(f"✅ 已创建 {len(clubs_data)} 个测试社团")

        # 创建测试学生
        students_data = [
            {
                "student_id": "2024001001",
                "name": "张三",
                "major": "计算机",
                "grade": "2024",
                "interest_scores": json.dumps({"arts": 30, "sports": 50, "academic": 60, "charity": 40, "tech": 95}),
                "time_available": json.dumps({"mon": ["evening"], "wed": ["evening"], "fri": ["afternoon", "evening"]}),
                "tags": "技术控"
            },
            {
                "student_id": "2024001002",
                "name": "李四",
                "major": "音乐",
                "grade": "2024",
                "interest_scores": json.dumps({"arts": 90, "sports": 30, "academic": 50, "charity": 60, "tech": 40}),
                "time_available": json.dumps({"tue": ["afternoon"], "thu": ["afternoon"], "sat": ["morning"]}),
                "tags": "文艺青年"
            },
            {
                "student_id": "2024001003",
                "name": "王五",
                "major": "体育",
                "grade": "2024",
                "interest_scores": json.dumps({"arts": 20, "sports": 95, "academic": 40, "charity": 50, "tech": 30}),
                "time_available": json.dumps({"mon": ["afternoon"], "wed": ["afternoon"], "sat": ["morning", "afternoon"]}),
                "tags": "运动达人"
            }
        ]

        for data in students_data:
            student = Student(**data)
            db.session.add(student)

        db.session.commit()
        print(f"✅ 已创建 {len(students_data)} 个测试学生")

        print("\n" + "="*50)
        print("🎉 初始化完成！")
        print("="*50)
        print("\n社团管理登录信息：")
        clubs = Club.query.all()
        for club in clubs:
            print(f"  - {club.name}: ID={club.id}, 密码={club.admin_password}")
        print("\n启动命令: python app.py")
        print("访问地址: http://127.0.0.1:5000")


if __name__ == '__main__':
    init_test_data()
