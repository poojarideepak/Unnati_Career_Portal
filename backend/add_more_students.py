import random
from database import SessionLocal, engine, Base
import models
import datetime

Base.metadata.create_all(bind=engine)
db = SessionLocal()

first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharva", "Rishi", "Nikhil", "Om", "Kabir", "Aryan", "Dhruv", "Pranav", "Rudra", "Ananya", "Myra", "Saanvi", "Aaradhya", "Diya", "Pari", "Anika", "Navya", "Avni", "Kavya", "Khushi", "Isha", "Kiara", "Prisha", "Riya", "Aahana", "Sarah", "Aashvi", "Aditi", "Ira"]
last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Bhatia", "Kumar", "Singh", "Patel", "Shah", "Reddy", "Nair", "Iyer", "Rao", "Joshi", "Chauhan", "Rajput", "Desai", "Mehta", "Bose", "Das", "Roy"]

skills_list = ["Marketing", "Excel", "Tally", "Accounting", "GST", "Java", "Python", "SQL", "Finance", "PowerBI", "Audit", "Communication", "C++", "JavaScript", "HTML", "CSS", "React"]

courses = ["BBA", "B.Com", "BCA"]

def generate_students():
    print("[INFO] Adding more students...")
    added_count = 0
    for course in courses:
        prefix = course.replace(".", "").upper()
        # Find highest roll no
        prefix_str = f"22{prefix}"
        existing = db.query(models.Student).filter(models.Student.course == course).all()
        existing_rolls = [s.roll_no for s in existing if s.roll_no.startswith(prefix_str)]
        max_num = 100
        if existing_rolls:
            nums = [int(r[-3:]) for r in existing_rolls if r[-3:].isdigit()]
            if nums:
                max_num = max(nums)
        
        for i in range(1, 51):
            max_num += 1
            roll_no = f"{prefix_str}{max_num:03d}"
            
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            
            day = random.randint(1, 28)
            month = random.randint(1, 12)
            year = random.randint(2000, 2003)
            dob = f"{day:02d}-{month:02d}-{year}"
            
            email = f"{fname.lower()}.{lname.lower()}{random.randint(1, 99)}@college.edu"
            phone = f"+91 {random.randint(9000000000, 9999999999)}"
            
            cgpa = round(random.uniform(5.5, 9.8), 1)
            
            course_skills = random.sample(skills_list, 3)
            skills = ", ".join(course_skills)
            
            batch = 2025
            is_placed = random.choice([True, False, False, False]) # 25% placed
            
            student = models.Student(
                name=name,
                roll_no=roll_no,
                dob=dob,
                email=email,
                phone=phone,
                course=course,
                cgpa=cgpa,
                skills=skills,
                batch=batch,
                is_placed=is_placed
            )
            db.add(student)
            added_count += 1
    
    db.commit()
    print(f"  [OK] {added_count} students added.")

if __name__ == "__main__":
    generate_students()
    db.close()
