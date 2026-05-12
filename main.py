from learning_coordinator import LearningCoordinator
import json
import os

def setup_sample_data(coordinator: LearningCoordinator):
    from models.learning import Subject, Topic, Question, Resource, DifficultyLevel
    
    math_subject = Subject(
        id="math",
        name="数学",
        description="中学数学课程",
        topics=["代数基础", "方程求解", "几何图形", "函数入门"]
    )
    coordinator.db_manager.save_subject(math_subject)
    
    topics = [
        Topic(id="math_algebra", name="代数基础", subject_id="math", 
              description="学习代数的基本概念和运算", difficulty=DifficultyLevel.EASY),
        Topic(id="math_equation", name="方程求解", subject_id="math", 
              description="学习一元一次方程和二元一次方程组", 
              prerequisites=["代数基础"], difficulty=DifficultyLevel.MEDIUM),
        Topic(id="math_geometry", name="几何图形", subject_id="math", 
              description="学习平面几何图形的性质和计算", difficulty=DifficultyLevel.MEDIUM),
        Topic(id="math_function", name="函数入门", subject_id="math", 
              description="学习函数的基本概念和图像", 
              prerequisites=["代数基础", "方程求解"], difficulty=DifficultyLevel.HARD)
    ]
    
    for topic in topics:
        coordinator.db_manager.save_topic(topic)
    
    questions = [
        Question(
            id="q1", topic_id="math_algebra",
            question_text="计算：2x + 3x = ?",
            options=["4x", "5x", "6x", "5x²"],
            correct_answer=1,
            explanation="同类项相加，系数相加：2x + 3x = (2+3)x = 5x",
            difficulty=DifficultyLevel.EASY
        ),
        Question(
            id="q2", topic_id="math_algebra",
            question_text="化简：3(a + 2b) - 2(a - b) = ?",
            options=["a + 4b", "a + 8b", "5a + 4b", "a + 2b"],
            correct_answer=1,
            explanation="3(a + 2b) - 2(a - b) = 3a + 6b - 2a + 2b = a + 8b",
            difficulty=DifficultyLevel.MEDIUM
        ),
        Question(
            id="q3", topic_id="math_equation",
            question_text="解方程：2x + 5 = 13",
            options=["x = 3", "x = 4", "x = 5", "x = 6"],
            correct_answer=1,
            explanation="2x = 13 - 5 = 8，所以x = 8 ÷ 2 = 4",
            difficulty=DifficultyLevel.EASY
        ),
        Question(
            id="q4", topic_id="math_equation",
            question_text="解方程：3(x - 2) = 2(x + 1)",
            options=["x = 6", "x = 8", "x = 10", "x = 4"],
            correct_answer=1,
            explanation="3x - 6 = 2x + 2，3x - 2x = 2 + 6，x = 8",
            difficulty=DifficultyLevel.MEDIUM
        ),
        Question(
            id="q5", topic_id="math_geometry",
            question_text="一个正方形的边长是5cm，它的面积是多少？",
            options=["20cm²", "25cm²", "30cm²", "35cm²"],
            correct_answer=1,
            explanation="正方形面积 = 边长 × 边长 = 5 × 5 = 25cm²",
            difficulty=DifficultyLevel.EASY
        ),
        Question(
            id="q6", topic_id="math_geometry",
            question_text="一个三角形的底是8cm，高是5cm，面积是多少？",
            options=["20cm²", "40cm²", "13cm²", "25cm²"],
            correct_answer=0,
            explanation="三角形面积 = 底 × 高 ÷ 2 = 8 × 5 ÷ 2 = 20cm²",
            difficulty=DifficultyLevel.EASY
        ),
        Question(
            id="q7", topic_id="math_function",
            question_text="函数y = 2x + 1的斜率是多少？",
            options=["1", "2", "-1", "-2"],
            correct_answer=1,
            explanation="一次函数y = kx + b中，k是斜率，所以斜率是2",
            difficulty=DifficultyLevel.EASY
        ),
        Question(
            id="q8", topic_id="math_function",
            question_text="函数y = x²的图像是什么形状？",
            options=["直线", "抛物线", "圆", "椭圆"],
            correct_answer=1,
            explanation="二次函数的图像是抛物线",
            difficulty=DifficultyLevel.MEDIUM
        )
    ]
    
    for question in questions:
        coordinator.db_manager.save_question(question)
    
    resources = [
        Resource(
            id="r1", topic_id="math_algebra",
            title="代数基础入门视频",
            type="video",
            url="https://example.com/algebra-intro",
            duration=10,
            difficulty=DifficultyLevel.EASY
        ),
        Resource(
            id="r2", topic_id="math_algebra",
            title="代数练习题",
            type="interactive",
            url="https://example.com/algebra-practice",
            difficulty=DifficultyLevel.MEDIUM
        ),
        Resource(
            id="r3", topic_id="math_equation",
            title="方程求解详解",
            type="video",
            url="https://example.com/equation-solving",
            duration=15,
            difficulty=DifficultyLevel.MEDIUM
        ),
        Resource(
            id="r4", topic_id="math_geometry",
            title="几何图形动画演示",
            type="video",
            url="https://example.com/geometry-animation",
            duration=12,
            difficulty=DifficultyLevel.EASY
        ),
        Resource(
            id="r5", topic_id="math_function",
            title="函数图像绘制工具",
            type="interactive",
            url="https://example.com/function-plotter",
            difficulty=DifficultyLevel.HARD
        )
    ]
    
    for resource in resources:
        coordinator.db_manager.save_resource(resource)

def main():
    coordinator = LearningCoordinator()
    
    setup_sample_data(coordinator)
    
    print("=== 个性化教育辅导Agent系统 ===")
    print("1. 注册学生")
    print("2. 学习诊断")
    print("3. 创建学习计划")
    print("4. 获取每日计划")
    print("5. 推荐学习资源")
    print("6. 推荐练习题")
    print("7. 提问答疑")
    print("8. 更新学习进度")
    print("9. 查看学习进度")
    print("10. 生成学习报告")
    print("11. 与同伴对比")
    print("0. 退出")
    
    while True:
        choice = input("\n请输入操作编号：")
        
        if choice == "1":
            student_id = input("学生ID：")
            name = input("姓名：")
            age = int(input("年龄："))
            grade = input("年级：")
            subjects = input("学科（逗号分隔）：").split(",")
            result = coordinator.register_student(student_id, name, age, grade, subjects)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "2":
            student_id = input("学生ID：")
            result = coordinator.diagnose_student(student_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "3":
            student_id = input("学生ID：")
            subject = input("学科：")
            result = coordinator.create_learning_plan(student_id, subject)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "4":
            student_id = input("学生ID：")
            subject = input("学科：")
            day = int(input("第几天："))
            result = coordinator.get_daily_plan(student_id, subject, day)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "5":
            student_id = input("学生ID：")
            subject = input("学科：")
            result = coordinator.recommend_resources(student_id, subject)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "6":
            student_id = input("学生ID：")
            subject = input("学科：")
            result = coordinator.recommend_questions(student_id, subject)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "7":
            student_id = input("学生ID：")
            question = input("问题：")
            subject = input("学科（可选）：") or None
            result = coordinator.ask_question(student_id, question, subject)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "8":
            student_id = input("学生ID：")
            subject = input("学科：")
            topic = input("主题：")
            score = float(input("分数："))
            completed = input("是否完成（y/n）：") == "y"
            result = coordinator.update_progress(student_id, subject, topic, score, completed)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "9":
            student_id = input("学生ID：")
            result = coordinator.get_progress(student_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "10":
            student_id = input("学生ID：")
            period = input("周期（week/month）：") or "week"
            result = coordinator.generate_report(student_id, period)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "11":
            student_id = input("学生ID：")
            subject = input("学科：")
            result = coordinator.compare_with_peers(student_id, subject)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif choice == "0":
            print("退出系统")
            break
        
        else:
            print("无效输入，请重新选择")

if __name__ == "__main__":
    main()