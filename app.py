from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
# from pydantic import BaseModel
# from typing import Optional, List
from sqlalchemy import create_engine, ForeignKey, Boolean, Column, String, Integer, PickleType, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.ext.mutable import MutableList


'''create app instance'''
app = Flask(__name__, template_folder='./templates', static_folder='./static')

'''SqlAlchemy Setup'''
SQLALCHEMY_DATABASE_URL = 'sqlite:///database.sqlite3:'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL


db = SQLAlchemy(app)


'''Database modals'''


class Student(db.Model):

    __tablename__ = 'student'

    student_id = Column(db.Integer, primary_key=True, index=True)
    roll_number = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    __table_args__ = (UniqueConstraint('student_id', 'roll_number'),
                      )


class Course(db.Model):

    __tablename__ = 'course'

    course_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), nullable=False)
    course_name = Column(String(50), nullable=False)
    course_description = Column(String())
    __table_args__ = (UniqueConstraint('course_id', 'course_code'),
                      )


class Enrollments(db.Model):

    __tablename__ = 'enrollments'

    enrollment_id = Column(Integer, primary_key=True, index=True)
    estudent_id = Column(String, ForeignKey('student.student_id'), nullable=False)
    ecourse_id = Column(String, ForeignKey('course.course_id'), nullable=False)


db.create_all()

course_data = [
    Course(course_id=1, course_code="CSE01",course_name="MAD I",course_description="Modern Application Development - I"),
    Course(course_id=2, course_code="CSE02",course_name="DBMS",course_description="Database management Systems"),
    Course(course_id=3, course_code="CSE03",course_name="PDSA",course_description="Data Structures and Algorithms using Python Programming"),
    Course(course_id=4, course_code="CSE04",course_name="BDM",course_description="Business Data Management")
]

if not Course.query.get(1):
    db.session.add_all(course_data)
    db.session.commit()


'''routes'''


@app.route('/', methods=['GET'])
def home():
    students = Student.query.all()
    print(students)
    return render_template('index.html', students=students, len=len)


@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == "POST":
        roll_number = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        course_id = request.form['courses']

        validation = Student.query.filter_by(roll_number=roll_number).first()
        if validation:
            return render_template('error.html', validation=validation)

        student_data = Student(roll_number=roll_number,
                               first_name=first_name,
                               last_name=last_name)

        '''save student data'''
        db.session.add(student_data)
        db.session.commit()

        student_id = student_data.student_id

        '''save enrollment'''
        enrollment_data = Enrollments(
            estudent_id=student_id,
            ecourse_id=course_id
            )
        db.session.add(enrollment_data)
        db.session.commit()

        print("Added student successfully.")

        if student_id:
            return redirect('/', code=200)
    return render_template('create_form.html')


@app.route('/student/<int:student_id>/update', methods=["GET", "PUT", "POST"])
def update_student(student_id):

    '''get db data'''
    student = Student.query.get(student_id)

    if request.method == "POST":
        '''get form data to update'''
        form_data = dict(request.form)
        first_name = form_data.get('f_name', None)
        last_name = form_data.get('l_name', None)
        course_id = form_data.get('courses', None)
        student.first_name = first_name
        student.last_name = last_name
        student.course_id = course_id
        '''update data'''
        db.session.commit()
        print("Updated student successfully.")

        if course_id:
            '''update enrollment data'''
            enrollment = Enrollments.query.filter_by(estudent_id=student_id).first()
            enrollment.course_id = course_id
            '''update data'''
            db.session.commit()

        return redirect('/', code=200)

    return render_template('update_form.html', student_data=student)


@app.route('/student/<int:student_id>', methods=['GET'])
def student_details(student_id):
    student_data = Student.query.get(student_id)
    enrollment_data = Enrollments.query.filter_by(estudent_id=student_id).all()
    print('==',enrollment_data)
    course_list = []
    for e in enrollment_data:
        print('==', e.ecourse_id)
        course_data = Course.query.get(e.ecourse_id)
        print('==++', course_data)
        course_list.append(course_data)
    return render_template('details.html', student_data=student_data, course_data=course_list)


@app.route('/student/<int:student_id>/delete', methods=['get', 'delete'])
def delete_record(student_id):
    student = Student.query.get(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect('/', code=200)


'''run application'''


if __name__ == "__main__":
    app.run(host='localhost', port=5006)
