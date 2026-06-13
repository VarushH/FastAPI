from fastapi import FastAPI,Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
import json


app = FastAPI()

def load_data():
    with open('students.json','r') as f:
        data = json.load(f)
        return data
    
def save_data(data):
    with open('students.json', 'w') as f:
        json.dump(data, f)
    
class Student(BaseModel):
    id: str
    name: str
    city: str
    age: int
    gender: str
    major: str
    gpa: float
    attendance: int
    verdict: str

class StudentUpdate(BaseModel):
    name: str
    city: str
    age: int
    gender: str
    major: str
    gpa: float
    attendance: int
    verdict: str

class CreateStudentRepsonse(BaseModel):
    message: str

@app.get("/")
def home():
    return "This is the home page"

@app.get("/health")
def health():
    return "App is Healthy"

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/student/{student_id}")
def view_student(student_id: str = Path(..., description = 'ID of the student in DB', example = 'P001')):
    #load all the student
    data = load_data()
    if student_id in data:
        return data[student_id]
    
    raise HTTPException(status_code=404,detail='Student not found')

@app.post('/create')
def create_student(student: Student):

    #load existing data
    data = load_data()

    #check if the student already exists
    if student.id in data:
        raise HTTPException(status_code = 400, detail = 'Student already exists')
    
    data[student.id] = student.model_dump(exclude=['id'])

    #save into the json file
    save_data(data)

    return CreateStudentRepsonse(
        message= 'Student added successfully'
    )

@app.put('/edit/{student_id}')
def update_student(student_id:str, student_update: StudentUpdate):

    #Load the existing data
    data = load_data()

    if student_id not in data:
        raise HTTPException(status_code=404, detail='Student not found')


    existing_student_info = data[student_id]

    updated_student_info = student_update.model_dump(exclude_unset=True)
    print(f'Updated Student Info {updated_student_info}')

    for key, value in updated_student_info.items():
        existing_student_info[key] = value

    existing_student_info['id'] = student_id
    student_pydandic_obj = Student(**existing_student_info)
    #-> pydantic object -> dict
    existing_student_info = student_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[student_id] = existing_student_info
    print(data[student_id])
    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'Student updated'})


@app.delete('/delete/{student_id}')
def delete_student(student_id: str):

    # load data
    data = load_data()

    if student_id not in data:
        raise HTTPException(status_code=404, detail='Student not found')
    
    del data[student_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'Student deleted'})