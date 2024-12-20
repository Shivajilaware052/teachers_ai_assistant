from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

# Initialize FastAPI
app = FastAPI()


# Database Configuration
DATABASE_URL = "postgresql://postgres:root@localhost:5433/students_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    score = Column(Integer, nullable=False)

# Create Tables
Base.metadata.create_all(bind=engine)

# Schemas
class StudentSchema(BaseModel):
    name: str

class SubjectSchema(BaseModel):
    name: str

class ScoreSchema(BaseModel):
    student_id: int
    subject_id: int
    score: int

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Management API"}

@app.post("/add-student/")
def add_student(student: StudentSchema):
    print(student)
    session = SessionLocal()
    new_student = Student(name=student.name)
    session.add(new_student)
    session.commit()
    session.close()
    return {"message": f"Student '{student.name}' added successfully."}

@app.post("/add-subject/")
def add_subject(subject: SubjectSchema):
    session = SessionLocal()
    new_subject = Subject(name=subject.name)
    session.add(new_subject)
    session.commit()
    session.close()
    return {"message": f"Subject '{subject.name}' added successfully."}

@app.post("/add-score/")
def add_score(score: ScoreSchema):
    session = SessionLocal()
    new_score = Score(
        student_id=score.student_id, 
        subject_id=score.subject_id, 
        score=score.score
    )
    session.add(new_score)
    session.commit()
    session.close()
    return {"message": f"Score {score.score} added successfully for student ID {score.student_id}."}


@app.get("/get-student/{student_name}")
def get_student_by_name(student_name: str):
    session = SessionLocal()

    # Get the student by name
    student = session.query(Student).filter(Student.name == student_name).first()
    
    if not student:
        session.close()
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Fetch all subjects and scores for the student
    student_scores = (
        session.query(Score, Subject)
        .join(Subject, Score.subject_id == Subject.id)
        .filter(Score.student_id == student.id)
        .all()
    )

    marks = [
        {"subject": subject.name, "score": score.score} for score, subject in student_scores
    ]
    
    session.close()

    # Return student info with marks and subjects
    return {
        "id": student.id,
        "name": student.name,
        "marks": marks
    }


@app.get("/get-all-students/")
def get_all_students():
    session = SessionLocal()
    students = session.query(Student).all()
    result = []

    for student in students:
        # Fetch scores and subjects for the student
        scores = (
            session.query(Score, Subject)
            .join(Subject, Score.subject_id == Subject.id)
            .filter(Score.student_id == student.id)
            .all()
        )
        marks = [
            {"subject": subject.name, "score": score.score} for score, subject in scores
        ]
        result.append({"id": student.id, "name": student.name, "marks": marks})

    session.close()

    if not result:
        raise HTTPException(status_code=404, detail="No students found")
    return result



@app.get("/summarize-scores/")
def summarize_scores(subject_name: str):
    session = SessionLocal()

    # Fetch the subject by name
    subject = session.query(Subject).filter(Subject.name == subject_name).first()
    if not subject:
        session.close()
        raise HTTPException(status_code=404, detail="Subject not found")

    # Fetch all scores for the given subject
    scores = session.query(Score).filter(Score.subject_id == subject.id).all()
    if not scores:
        session.close()
        raise HTTPException(status_code=404, detail="No scores found for this subject")

    # Calculate the average score for the subject
    total_score = sum(score.score for score in scores)
    average_score = total_score / len(scores)

    session.close()

    return {
        "subject": subject_name,
        "average_score": average_score,
        "number_of_scores": len(scores)
    }
    
    

@app.get("/get-subjects/")
def get_subjects(student_name: str):
    session = SessionLocal()

    # Fetch the student by name
    student = session.query(Student).filter(Student.name == student_name).first()
    if not student:
        session.close()
        raise HTTPException(status_code=404, detail="Student not found")

    # Retrieve the list of subjects this student has taken
    subjects = (
        session.query(Subject)
        .join(Score, Score.subject_id == Subject.id)
        .filter(Score.student_id == student.id)
        .all()
    )

    session.close()

    if not subjects:
        raise HTTPException(status_code=404, detail="No subjects found for this student")

    return {
        "student_name": student_name,
        "subjects": [subject.name for subject in subjects]
    }
    
    
@app.get("/get-all-subjects/")
def get_all_subjects():
    session = SessionLocal()

    # Retrieve all subjects
    subjects = session.query(Subject).all()

    session.close()

    if not subjects:
        raise HTTPException(status_code=404, detail="No subjects found")

    return {
        "subjects": [{"id": subject.id, "name": subject.name} for subject in subjects]
    }
