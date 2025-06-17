#!/usr/bin/env python
# coding: utf-8

# In[7]:


#import libraries as needed
get_ipython().system('pip install pymongo')
from pymongo import MongoClient
from pymongo import MongoClient
from datetime import datetime
import pandas as pd


# In[6]:


#upgrade of pip
import sys
get_ipython().system('{sys.executable} -m pip install --upgrade pip')


# In[8]:


#Initializing the database
client = MongoClient('mongodb://localhost:27017/')
db = client['eduhub_db']


# In[48]:


#user document schema

users_schema = {
    "_id": "ObjectId (auto-generated)",

    "firstName": "string (required)",
    "lastName": "string (required)",
    "email": "string (required)",

    "role": "string (enum: ['student', 'instructor'])",

    "dateJoined": "datetime (optional)",

    "profile": {
        "bio": "string (optional)",
        "avatar": "string (optional)",
        "skills": ["string"]  # optional array of strings
    },

    "isActive": "boolean (optional)"
}


# In[49]:


users_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["firstName", "lastName", "email", "role"],
        "properties": {
            "firstName": {"bsonType": "string"},
            "lastName": {"bsonType": "string"},
            "email": {"bsonType": "string"},
            "role": {"enum": ["student", "instructor"]},
            "dateJoined": {"bsonType": "date"},
            "profile": {
                "bsonType": "object",
                "properties": {
                    "bio": {"bsonType": "string"},
                    "avatar": {"bsonType": "string"},
                    "skills": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    }
                }
            },
            "isActive": {"bsonType": "bool"}
        }
    }
}


# In[24]:


course_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["courseId", "title", "instructorId", "level", "duration", "price", "createdAt", "updatedAt", "isPublished"],
        "properties": {
            "courseId": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "description": {"bsonType": "string"},
            "instructorId": {"bsonType": "string"},  # referencing user.userId
            "category": {"bsonType": "string"},
            "level": {"enum": ["beginner", "intermediate", "advanced"]},
            "duration": {"bsonType": ["double", "int"]},  # to handle both 8.2 and 8
            "price": {"bsonType": ["double", "int"]},
            "tags": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "createdAt": {"bsonType": "date"},
            "updatedAt": {"bsonType": "date"},
            "isPublished": {"bsonType": "bool"}
        }
    }
}

# Apply this validator to the 'courses' collection
db.command({
    "collMod": "courses",
    "validator": course_validator,
    "validationLevel": "moderate"
})


# In[14]:


course_schema = {

    "_id": "ObjectId (auto-generated)",

    "courseId": "string (unique)",

    "title": "string (required)",

    "description": "string",

    "instructorId": "string (reference to users)",

    "category": "string",

    "level": "string (enum: [‘beginner’, ‘intermediate’, ‘advanced’])",

    "duration": "number (in hours)",

    "price": "number",

    "tags": ["string"],

    "createdAt": "datetime",

    "updatedAt": "datetime",

    "isPublished": "boolean"

}


# In[27]:


# Enrollments collection
enrollment_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["enrollmentId", "studentId", "courseId", "enrolledAt", "progress", "status"],
        "properties": {
            "enrollmentId": {"bsonType": "string"},
            "studentId": {"bsonType": "string"},  # Should match users.userId
            "courseId": {"bsonType": "string"},   # Should match courses.courseId
            "enrolledAt": {"bsonType": "date"},
            "progress": {
                "bsonType": ["int", "double"],
                "minimum": 0,
                "maximum": 100
            },
            "status": {
                "enum": ["enrolled", "completed", "dropped"]
            }
        }
    }
}

# Apply the validator to the enrollments collection
db.command({
    "collMod": "enrollments",
    "validator": enrollment_validator,
    "validationLevel": "moderate"
})


# In[ ]:


enrollment_schema = {
    "_id": "ObjectId (auto-generated)",

    "enrollmentId": "string (unique)",

    "studentId": "string (reference to users.userId)",

    "courseId": "string (reference to courses.courseId)",

    "enrolledAt": "datetime",

    "progress": "number (percentage, e.g., 75)",

    "status": "string (enum: ['enrolled', 'completed', 'dropped'])"
}


# In[29]:


lesson_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["lessonId", "courseId", "title", "content", "position", "createdAt", "updatedAt"],
        "properties": {
            "lessonId": {"bsonType": "string"},
            "courseId": {"bsonType": "string"},  # Reference to courses.courseId
            "title": {"bsonType": "string"},
            "content": {"bsonType": "string"},   # Can contain HTML or markdown
            "videoUrl": {
                "bsonType": "string"
            },
            "position": {
                "bsonType": ["int", "double"],
                "minimum": 1
            },
            "createdAt": {"bsonType": "date"},
            "updatedAt": {"bsonType": "date"}
        }
    }
}

# Apply the validator to the lessons collection
db.command({
    "collMod": "lessons",
    "validator": lesson_validator,
    "validationLevel": "moderate"
})


# In[ ]:


lesson_schema = {
    "_id": "ObjectId (auto-generated)",

    "lessonId": "string (unique)",

    "courseId": "string (reference to courses.courseId)",

    "title": "string (required)",

    "content": "string (HTML or markdown)",

    "videoUrl": "string (optional)",

    "position": "number (order in course)",

    "createdAt": "datetime",

    "updatedAt": "datetime"
}


# In[31]:


#Assignment validator
assignment_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["assignmentId", "courseId", "title", "dueDate", "totalMarks", "createdAt", "updatedAt"],
        "properties": {
            "assignmentId": {"bsonType": "string"},
            "courseId": {"bsonType": "string"},  # Reference to courses.courseId
            "title": {"bsonType": "string"},
            "description": {"bsonType": "string"},
            "dueDate": {"bsonType": "date"},
            "totalMarks": {
                "bsonType": ["int", "double"],
                "minimum": 0
            },
            "createdAt": {"bsonType": "date"},
            "updatedAt": {"bsonType": "date"}
        }
    }
}

# Apply the validator to the assignments collection
db.command({
    "collMod": "assignments",
    "validator": assignment_validator,
    "validationLevel": "moderate"
})


# In[ ]:


assignment_schema = {
    "_id": "ObjectId (auto-generated)",

    "assignmentId": "string (unique)",

    "courseId": "string (reference to courses.courseId)",

    "title": "string (required)",

    "description": "string",

    "dueDate": "datetime",

    "totalMarks": "number",

    "createdAt": "datetime",

    "updatedAt": "datetime"
}


# In[35]:


#Submission validator
submission_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "submissionId",
            "assignmentId",
            "studentId",
            "submittedAt",
            "content",
            "status"
        ],
        "properties": {
            "submissionId": {"bsonType": "string"},
            "assignmentId": {"bsonType": "string"},
            "studentId": {"bsonType": "string"},
            "submittedAt": {"bsonType": "date"},
            "content": {"bsonType": "string"},
            "grade": {
                "bsonType": "object",
                "properties": {
                    "score": {
                        "bsonType": ["int", "double"],
                        "minimum": 0
                    },
                    "feedback": {"bsonType": "string"},
                    "gradedAt": {"bsonType": "date"},
                    "gradedBy": {"bsonType": "string"}
                }
            },
            "status": {
                "enum": ["submitted", "graded", "late"]
            }
        }
    }
}


# In[ ]:


submission_schema = {
    "_id": "ObjectId (auto-generated)",

    "submissionId": "string (unique)",

    "assignmentId": "string (reference to assignments.assignmentId)",

    "studentId": "string (reference to users.userId)",

    "submittedAt": "datetime",

    "content": "string (URL, text, or file reference)",

    "grade": {
        "score": "number",
        "feedback": "string",
        "gradedAt": "datetime",
        "gradedBy": "string (instructorId)"
    },

    "status": "string (enum: ['submitted', 'graded', 'late'])"
}


# In[16]:


import random
import uuid


# In[20]:


db.command({
    "collMod": "users",
    "validator": user_validator,
    "validationLevel": "moderate"
})


# In[122]:


import pandas as pd


# In[ ]:


#insert users
from datetime import datetime
import random
import uuid

roles = ['student', 'instructor']
users = []

for i in range(20):
    role = random.choice(roles)
    user = {
        "userId": str(uuid.uuid4()),
        "email": f"user{i}@eduhub.com",
        "firstName": f"First{i}",
        "lastName": f"Last{i}",
        "role": role,
        "dateJoined": datetime.now(),
        "profile": {
            "bio": f"This is user {i}'s bio.",
            "avatar": f"https://avatar.com/u{i}.png",
            "skills": ["Python", "Data", "Web"][0:random.randint(1, 3)]
        },
        "isActive": True
    }
    users.append(user)

# Insert into MongoDB
db.users.insert_many(users)


# In[25]:


#Insert Courses

course_levels = ['beginner', 'intermediate', 'advanced']
categories = ['Data Science', 'Web Dev', 'AI', 'Cloud']
instructors = [u for u in users if u['role'] == 'instructor']
courses = []

for i in range(8):
    instructor = random.choice(instructors)
    course = {
        "courseId": str(uuid.uuid4()),
        "title": f"Course {i}",
        "description": f"This is course {i} description.",
        "instructorId": instructor["userId"],
        "category": random.choice(categories),
        "level": random.choice(course_levels),
        "duration": round(random.uniform(1.5, 10), 1),
        "price": round(random.uniform(10, 200), 2),
        "tags": ["tech", "edu", "skill"][0:random.randint(1, 3)],
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "isPublished": True
    }
    courses.append(course)

db.courses.insert_many(courses)


# In[28]:


#Insert enrollments
students = [u for u in users if u['role'] == 'student']
enrollments = []

for i in range(15):
    enrollment = {
        "enrollmentId": str(uuid.uuid4()),
        "studentId": random.choice(students)["userId"],
        "courseId": random.choice(courses)["courseId"],
        "enrolledAt": datetime.now(),
        "progress": random.randint(0, 100),
        "status": random.choice(['enrolled', 'completed', 'dropped'])
    }
    enrollments.append(enrollment)

db.enrollments.insert_many(enrollments)


# In[30]:


#insert Lesson
lessons = []

for i in range(25):
    course = random.choice(courses)
    lesson = {
        "lessonId": str(uuid.uuid4()),
        "courseId": course["courseId"],
        "title": f"Lesson {i}",
        "content": f"Lesson {i} content in markdown or HTML.",
        "videoUrl": f"https://videos.com/lesson{i}",
        "position": random.randint(1, 10),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    lessons.append(lesson)

db.lessons.insert_many(lessons)


# In[32]:


#Insert assignment
assignments = []

for i in range(10):
    course = random.choice(courses)
    assignment = {
        "assignmentId": str(uuid.uuid4()),
        "courseId": course["courseId"],
        "title": f"Assignment {i}",
        "description": f"This is the description for assignment {i}.",
        "dueDate": datetime(2025, 12, 31),
        "totalMarks": 100,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    assignments.append(assignment)

db.assignments.insert_many(assignments)


# In[36]:


#insert submission
submissions = []

for i in range(12):
    assignment = random.choice(assignments)
    student = random.choice(students)
    graded = random.choice([True, False])

    submission = {
        "submissionId": str(uuid.uuid4()),
        "assignmentId": assignment["assignmentId"],
        "studentId": student["userId"],
        "submittedAt": datetime.now(),
        "content": f"https://submissions.com/s{i}",
        "status": "graded" if graded else "submitted"
    }

    if graded:
        submission["grade"] = {
            "score": random.randint(0, 100),
            "feedback": "Good job!",
            "gradedAt": datetime.now(),
            "gradedBy": random.choice(instructors)["userId"]
        }

    submissions.append(submission)

db.submissions.insert_many(submissions)


# In[39]:


# 3. Create collections with validation rules
def create_or_update_collection(name, validator):
    if name in db.list_collection_names():
        # Collection exists: update validator
        db.command({
            "collMod": name,
            "validator": validator,
            "validationLevel": "moderate"  # or "strict" if you prefer
        })
        print(f"Updated validator for existing collection: {name}")
    else:
        # Create new collection with validator
        db.create_collection(name, validator=validator)
        print(f"Created new collection with validator: {name}")


# Apply to all your collections
create_or_update_collection("user", user_validator)
create_or_update_collection("courses", course_validator)
create_or_update_collection("enrollments", enrollment_validator)
create_or_update_collection("lessons", lesson_validator)
create_or_update_collection("assignments", assignment_validator)
create_or_update_collection("submissions", submission_validator)

print("All collections created or updated successfully.")


# In[42]:


collections = db.list_collection_names()

print("Collections in 'eduhub_db':")
for col in collections:
    print(f" - {col}")


# In[46]:


# Delete 'user' collection if it exists
if "user" in db.list_collection_names():
    db.user.drop()
    print("Dropped 'user' collection.")

# Delete 'users' collection if it exists
if "users" in db.list_collection_names():
    db.users.drop()
    print("Dropped 'users' collection.")


# In[51]:


collections = db.list_collection_names()

print("Collections in 'eduhub_db':")
for col in collections:
    print(f" - {col}")


# In[55]:


from pprint import pprint

# Retrieve all documents from the 'users' collection
users = db.users.find()

# Print each user document
print("Documents in 'users' collection:")
for user in users:
    pprint(user)


# In[56]:


#Basic CRUD Operations, task3.1
# 1. Add a new student user (append to existing users)
new_student = {
    "userId": str(uuid.uuid4()),
    "firstName": "Ada",
    "lastName": "Okoro",
    "email": "ada.okoro@example.com",
    "role": "student",
    "dateJoined": datetime.now(),
    "profile": {
        "bio": "A passionate learner",
        "avatar": "https://example.com/avatar.png",
        "skills": ["Python", "MongoDB"]
    },
    "isActive": True
}
db.users.insert_one(new_student)
print("✅ New student user added.")


# In[57]:


# 2. Create a new course (append to existing courses)
# Ensure there’s at least one instructor to assign
instructor = db.users.find_one({"role": "instructor"})
if not instructor:
    raise Exception("No instructor found. Add one first.")

new_course = {
    "courseId": str(uuid.uuid4()),
    "title": "Data Visualization with Python",
    "description": "Learn how to visualize data using matplotlib and seaborn.",
    "instructorId": instructor["userId"],
    "category": "Data Science",
    "level": "intermediate",
    "duration": 5.5,
    "price": 89.99,
    "tags": ["data", "visualization", "python"],
    "createdAt": datetime.now(),
    "updatedAt": datetime.now(),
    "isPublished": True
}
db.courses.insert_one(new_course)
print("✅ New course added.")


# In[58]:


# 3. Enroll the new student in the new course (append to enrollments)
new_enrollment = {
    "enrollmentId": str(uuid.uuid4()),
    "studentId": new_student["userId"],
    "courseId": new_course["courseId"],
    "enrolledAt": datetime.now(),
    "progress": 0,
    "status": "enrolled"
}
db.enrollments.insert_one(new_enrollment)
print("✅ Student enrolled in course.")


# In[59]:


# 4. Add a new lesson to the existing course (append to lessons)
new_lesson = {
    "lessonId": str(uuid.uuid4()),
    "courseId": new_course["courseId"],
    "title": "Lesson 1: Introduction to Data Visualization",
    "content": "<p>This lesson covers the basics of data visualization using Python libraries.</p>",
    "videoUrl": "https://videos.example.com/lesson1",
    "position": 1,
    "createdAt": datetime.now(),
    "updatedAt": datetime.now()
}
db.lessons.insert_one(new_lesson)
print("✅ New lesson added to course.")


# In[61]:


import re


# In[62]:


#Task 3.2 Read Operations
# 1. Find all active students
active_students = list(db.users.find({
    "role": "student",
    "isActive": True
}))
print("✅ Active students:")
for student in active_students:
    print(f"- {student['firstName']} {student['lastName']}")

# 2. Retrieve course details with instructor information (using aggregation)
courses_with_instructors = list(db.courses.aggregate([
    {
        "$lookup": {
            "from": "users",
            "localField": "instructorId",
            "foreignField": "userId",
            "as": "instructor"
        }
    },
    {"$unwind": "$instructor"}
]))
print("\n✅ Courses with instructor details:")
for course in courses_with_instructors:
    print(f"- {course['title']} by {course['instructor']['firstName']} {course['instructor']['lastName']}")

# 3. Get all courses in a specific category (e.g., "Data Science")
category = "Data Science"
data_science_courses = list(db.courses.find({
    "category": category
}))
print(f"\n✅ Courses in category '{category}':")
for course in data_science_courses:
    print(f"- {course['title']}")

# 4. Find students enrolled in a particular course
# Example: using a specific courseId
course_id = courses_with_instructors[0]["courseId"]  # just taking the first course
enrollments = list(db.enrollments.find({
    "courseId": course_id
}))

student_ids = [e["studentId"] for e in enrollments]
students_in_course = list(db.users.find({
    "userId": {"$in": student_ids}
}))

print(f"\n✅ Students enrolled in course '{courses_with_instructors[0]['title']}':")
for student in students_in_course:
    print(f"- {student['firstName']} {student['lastName']}")

# 5. Search courses by title (case-insensitive, partial match)
search_term = "python"
matched_courses = list(db.courses.find({
    "title": {"$regex": re.compile(search_term, re.IGNORECASE)}
}))
print(f"\n✅ Courses matching '{search_term}' in title:")
for course in matched_courses:
    print(f"- {course['title']}")


# In[63]:


#Task 3.3 Update Operations
db.users.update_one(
    {"email": "user1@eduhub.com"},
    {
        "$set": {
            "profile.bio": "Updated bio for user1.",
            "profile.avatar": "https://new-avatar.com/u1.png"
        }
    }
)


#Mark a course as published
db.courses.update_one(
    {"title": "Course 3"},
    {"$set": {"isPublished": True}}
)


#Add tags to an existing course

db.courses.update_one(
    {"title": "Course 5"},
    {
        "$addToSet": {
            "tags": {"$each": ["project", "practical"]}
        }
    }
)


# In[64]:


#Task3.4 Delete operation
#1 Remove a user
db.users.update_one(
    {"email": "student1@eduhub.com"},
    {"$set": {"isActive": False}}
)

#2 Delete enrollment
db.enrollments.delete_one(
    {"enrollmentId": "your-enrollment-id-here"}
)
#3 Remove lesson from course
db.lessons.delete_one(
    {"lessonId": "your-lesson-id-here"}
)


# In[65]:


#Task 4.1.1; complex queries
courses_in_range = list(db.courses.find({
    "price": {"$gte": 50, "$lte": 200}
}))

print("Courses priced between $50 and $200:")
for course in courses_in_range:
    print(course["title"], "-", course["price"])


# In[66]:


#Task 4.1.2 users who joined in the last 6months

from datetime import datetime, timedelta

six_months_ago = datetime.now() - timedelta(days=6*30)  # approximate 6 months
recent_users = list(db.users.find({
    "dateJoined": {"$gte": six_months_ago}
}))

print("\nUsers who joined in the last 6 months:")
for user in recent_users:
    print(user["firstName"], user["lastName"], "-", user["dateJoined"])


# In[67]:


#Task 4.1.3 Find courses that have specific tags using $in operator
tags_to_find = ["tech", "python", "cloud"]

courses_with_tags = list(db.courses.find({
    "tags": {"$in": tags_to_find}
}))

print("\nCourses with specified tags:")
for course in courses_with_tags:
    print(course["title"], "-", course["tags"])


# In[68]:


#Task 4.1.4 Retrieve assignment with due dates in the next week
today = datetime.now()
next_week = today + timedelta(days=7)

upcoming_assignments = list(db.assignments.find({
    "dueDate": {"$gte": today, "$lte": next_week}
}))

print("\nAssignments due in the next 7 days:")
for assignment in upcoming_assignments:
    print(assignment["title"], "-", assignment["dueDate"])


# In[69]:


#Task 4.2.1 Count total enrollment per course
pipeline_enrollments_per_course = [
    {
        "$group": {
            "_id": "$courseId",
            "totalEnrollments": {"$sum": 1}
        }
    },
    {
        "$lookup": {
            "from": "courses",
            "localField": "_id",
            "foreignField": "courseId",
            "as": "courseDetails"
        }
    },
    {
        "$unwind": "$courseDetails"
    },
    {
        "$project": {
            "courseTitle": "$courseDetails.title",
            "totalEnrollments": 1
        }
    }
]

results = db.enrollments.aggregate(pipeline_enrollments_per_course)

print("Total enrollments per course:")
for doc in results:
    print(f"{doc['courseTitle']} → {doc['totalEnrollments']} enrollments")


# In[71]:


#Task 4.2.1 Average course rating
pipeline_avg_rating = [
    {
        "$project": {
            "title": 1,
            "avgRating": {"$avg": "$ratings"}
        }
    }
]

results = db.courses.aggregate(pipeline_avg_rating)

print("\n Average rating per course:")
for doc in results:
    print(f"{doc['title']} → {round(doc['avgRating'], 2) if doc['avgRating'] else 'No ratings'}")


# In[72]:


#Task 4.2.1 Group by course category
pipeline_group_by_category = [
    {
        "$group": {
            "_id": "$category",
            "totalCourses": {"$sum": 1}
        }
    },
    {
        "$sort": {"totalCourses": -1}
    }
]

results = db.courses.aggregate(pipeline_group_by_category)

print("\n Total courses by category:")
for doc in results:
    print(f"{doc['_id']} → {doc['totalCourses']} courses")


# In[74]:


#Task 4.2.2 Average grade per student
pipeline_avg_grade_per_student = [
    {
        "$match": {
            "grade.score": {"$ne": None}
        }
    },
    {
        "$group": {
            "_id": "$studentId",
            "averageGrade": {"$avg": "$grade.score"}
        }
    },
    {
        "$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "userId",
            "as": "student"
        }
    },
    {"$unwind": "$student"},
    {
        "$project": {
            "studentName": {
                "$concat": ["$student.firstName", " ", "$student.lastName"]
            },
            "averageGrade": 1
        }
    },
    {"$sort": {"averageGrade": -1}}
]

results = db.submissions.aggregate(pipeline_avg_grade_per_student)

print("\n Average grade per student:")
for doc in results:
    print(f"{doc['studentName']} → {round(doc['averageGrade'], 2)}%")



# In[75]:


#Task 4.2.2 Completion rate by course
pipeline_completion_rate = [
    {
        "$group": {
            "_id": "$courseId",
            "total": {"$sum": 1},
            "completed": {
                "$sum": {
                    "$cond": [{"$eq": ["$status", "completed"]}, 1, 0]
                }
            }
        }
    },
    {
        "$project": {
            "completionRate": {
                "$cond": [
                    {"$eq": ["$total", 0]},
                    0,
                    {"$multiply": [{"$divide": ["$completed", "$total"]}, 100]}
                ]
            }
        }
    },
    {
        "$lookup": {
            "from": "courses",
            "localField": "_id",
            "foreignField": "courseId",
            "as": "course"
        }
    },
    {"$unwind": "$course"},
    {
        "$project": {
            "courseTitle": "$course.title",
            "completionRate": 1
        }
    },
    {"$sort": {"completionRate": -1}}
]

results = db.enrollments.aggregate(pipeline_completion_rate)

print("\nCompletion rate by course:")
for doc in results:
    print(f"{doc['courseTitle']} → {round(doc['completionRate'], 2)}%")


# In[82]:


#inserting extraa submissions
from datetime import datetime
import uuid
import random

instructors = list(db.users.find({"role": "instructor"}))
students = list(db.users.find({"role": "student"}))
assignments = list(db.assignments.find())

submissions = []

for i in range(12):
    assignment = random.choice(assignments)
    student = random.choice(students)

    # Force all to be graded
    submission = {
        "submissionId": str(uuid.uuid4()),
        "assignmentId": assignment["assignmentId"],
        "studentId": student["userId"],
        "submittedAt": datetime.now(),
        "content": f"https://submissions.com/s{i}",
        "grade": {
            "score": random.randint(60, 100),
            "feedback": "Nice work!",
            "gradedAt": datetime.now(),
            "gradedBy": random.choice(instructors)["userId"]
        },
        "status": "graded"
    }

    submissions.append(submission)

db.submissions.insert_many(submissions)
print("Sample graded submissions inserted.")


# In[84]:


#Task 4.2.2 Top performing Students
from bson.son import SON

pipeline_top_students = [
    { "$match": { "grade.score": { "$ne": None } } },
    { "$group": {
        "_id": "$studentId",
        "averageGrade": { "$avg": "$grade.score" }
    }},
    { "$lookup": {
        "from": "users",
        "localField": "_id",
        "foreignField": "userId",
        "as": "studentInfo"
    }},
    { "$unwind": "$studentInfo" },
    { "$addFields": {
        "studentName": {
            "$concat": ["$studentInfo.firstName", " ", "$studentInfo.lastName"]
        }
    }},
    { "$sort": SON([("averageGrade", -1)]) },
    { "$limit": 5 }
]

results = db.submissions.aggregate(pipeline_top_students)

print("\nTop 5 performing students:")
for doc in results:
    print(f"{doc['studentName']} → {round(doc['averageGrade'], 2)}%")


# In[85]:


#Task 4.2.3 Total student taught by each instructor
pipeline_total_students_per_instructor = [
    {
        "$lookup": {
            "from": "courses",
            "localField": "courseId",
            "foreignField": "courseId",
            "as": "course"
        }
    },
    {"$unwind": "$course"},
    {
        "$group": {
            "_id": "$course.instructorId",
            "uniqueStudents": {"$addToSet": "$studentId"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "instructorId": "$_id",
            "totalStudents": {"$size": "$uniqueStudents"}
        }
    }
]

results = db.enrollments.aggregate(pipeline_total_students_per_instructor)
print("\nTotal students per instructor:")
for doc in results:
    print(doc)


# In[86]:


#Task 4.2.3 Average course rating per instructor
pipeline_avg_rating_per_instructor = [
    {
        "$group": {
            "_id": "$instructorId",
            "averageRating": {"$avg": "$rating"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "instructorId": "$_id",
            "averageRating": {"$round": ["$averageRating", 2]}
        }
    }
]

results = db.courses.aggregate(pipeline_avg_rating_per_instructor)
print("\nAverage course rating per instructor:")
for doc in results:
    print(doc)


# In[87]:


#Task 4.2.3 Revenue generated by instructor
pipeline_revenue_per_instructor = [
    {
        "$lookup": {
            "from": "courses",
            "localField": "courseId",
            "foreignField": "courseId",
            "as": "course"
        }
    },
    {"$unwind": "$course"},
    {
        "$group": {
            "_id": "$course.instructorId",
            "totalRevenue": {"$sum": "$course.price"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "instructorId": "$_id",
            "totalRevenue": {"$round": ["$totalRevenue", 2]}
        }
    }
]

results = db.enrollments.aggregate(pipeline_revenue_per_instructor)
print("\nRevenue per instructor:")
for doc in results:
    print(doc)



# In[88]:


#task 4.2.4 Monthly enrollment trends
pipeline_monthly_enrollments = [
    {
        "$group": {
            "_id": {
                "year": {"$year": "$enrolledAt"},
                "month": {"$month": "$enrolledAt"}
            },
            "enrollmentCount": {"$sum": 1}
        }
    },
    {"$sort": {"_id.year": 1, "_id.month": 1}},
    {
        "$project": {
            "_id": 0,
            "year": "$_id.year",
            "month": "$_id.month",
            "enrollmentCount": 1
        }
    }
]

results = db.enrollments.aggregate(pipeline_monthly_enrollments)
print("\nMonthly Enrollment Trends:")
for doc in results:
    print(doc)


# In[89]:


#Task 4.2.4 Most popular course categories
pipeline_popular_categories = [
    {
        "$lookup": {
            "from": "courses",
            "localField": "courseId",
            "foreignField": "courseId",
            "as": "course"
        }
    },
    {"$unwind": "$course"},
    {
        "$group": {
            "_id": "$course.category",
            "totalEnrollments": {"$sum": 1}
        }
    },
    {"$sort": {"totalEnrollments": -1}},
    {
        "$project": {
            "_id": 0,
            "category": "$_id",
            "totalEnrollments": 1
        }
    }
]

results = db.enrollments.aggregate(pipeline_popular_categories)
print("\nMost Popular Course Categories:")
for doc in results:
    print(doc)


# In[91]:


#Task 4.2.4 Student engagement
# Submissions per student
pipeline_engagement = [
    {
        "$group": {
            "_id": "$studentId",
            "submissions": {"$sum": 1}
        }
    },
    {
        "$project": {
            "_id": 0,
            "studentId": "$_id",
            "submissions": 1
        }
    },
    {"$sort": {"submissions": -1}}
]

results = db.submissions.aggregate(pipeline_engagement)
print("\nStudent Engagement (Submissions per Student):")
for doc in results:
    print(doc)

# Completion rate (students who completed a course / total enrolled)
pipeline_completion_rate = [
    {
        "$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }
    }
]

results = list(db.enrollments.aggregate(pipeline_completion_rate))
total = sum(doc["count"] for doc in results)
completed = next((doc["count"] for doc in results if doc["_id"] == "completed"), 0)
completion_rate = (completed / total) * 100 if total else 0
print(f"\nOverall Course Completion Rate: {round(completion_rate, 2)}%")


# In[92]:


#Task 5.1.1 Index creation: User Email LookUP
db.users.create_index("email", unique=True)


# In[93]:


#Task 5.1.2 Course search by title and category
db.courses.create_index([("title", 1), ("category", 1)])


# In[94]:


#Task 5.1.3 Assignment queries by due date
db.assignments.create_index("dueDate")


# In[95]:


#Task 5.1.4 enrollment Enrollment queries by student and course
db.enrollments.create_index([("studentId", 1), ("courseId", 1)])


# In[97]:


#Task 5.2.1 Query performance with explain()
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["eduhub_db"]

# Example: Find a user by email
explanation = db.users.find({"email": "student@example.com"}).explain()
print(explanation)


# In[100]:


#Task 5.2.2 Optimize 3 slow queries, 1
import time
def time_query(label, query_func):
    start = time.time()
    result = query_func()
    end = time.time()
    duration = round(end - start, 4)
    print(f"{label} → {duration} seconds")
    return result

# Create index (if not yet created)
db.users.create_index("email", unique=True)

# Define the query function
def query_user_by_email():
    return list(db.users.find({"email": "student@example.com"}))

# Run with timer
time_query("User Email Lookup", query_user_by_email)


# In[101]:


#Task 5.2.2 Optimize 3 slow queries, 2
db.courses.create_index([("title", "text"), ("category", "text")])

# Define the text search function
def search_courses_by_title():
    return list(db.courses.find({"$text": {"$search": "python"}}))

# Run with timer
time_query("Course Title Search", search_courses_by_title)


# In[102]:


#Task 5.2.2 Optimize 3 slow queries, 3
# Ensure index exists
db.assignments.create_index("dueDate")

# Define the time-based query
def upcoming_assignments():
    next_week = datetime.now() + timedelta(days=7)
    return list(db.assignments.find({"dueDate": {"$lte": next_week}}))

# Run with timer
time_query("Assignments Due in 7 Days", upcoming_assignments)


# In[103]:


#Task 6.1 Schema validation. 
#Ths handles missing email (required field),wrong role value(not in student  or instructor)
#This handles invalid email like test@com (rejection reason is if it fails regex)
#This handles skills not an array(rejection reason is TYPE mismatch)
#This handles dateJoined as string (rejection reason will be TYPE mismatch)

user_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["firstName", "lastName", "email", "role"],
        "properties": {
            "firstName": {
                "bsonType": "string",
                "description": "Must be a string and is required"
            },
            "lastName": {
                "bsonType": "string",
                "description": "Must be a string and is required"
            },
            "email": {
                "bsonType": "string",
                "pattern": "^\\S+@\\S+\\.\\S+$",
                "description": "Must be a valid email address"
            },
            "role": {
                "enum": ["student", "instructor"],
                "description": "Can only be 'student' or 'instructor'"
            },
            "dateJoined": {
                "bsonType": "date",
                "description": "Must be a date"
            },
            "profile": {
                "bsonType": "object",
                "properties": {
                    "bio": {"bsonType": "string"},
                    "avatar": {"bsonType": "string"},
                    "skills": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    }
                }
            },
            "isActive": {
                "bsonType": "bool",
                "description": "Must be true or false"
            }
        }
    }
}


# In[109]:


#Task 6.2
from pymongo import MongoClient, errors
from datetime import datetime


# In[112]:


#Export all collections to sample_data.json
from pymongo import MongoClient
from bson.json_util import dumps
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['eduhub_db']

# List all collections
collections = db.list_collection_names()

# Export data from each collection
export_data = {}

for coll_name in collections:
    data = list(db[coll_name].find())
    export_data[coll_name] = data

# Write to JSON file
with open("sample_data.json", "w") as f:
    f.write(dumps(export_data, indent=2))

print("Exported all collection data to 'sample_data.json'")


# In[113]:


#Export of each collection to a folder "Sample_data_exports"
from pymongo import MongoClient
from bson.json_util import dumps
import os

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['eduhub_db']

# Create output directory (if not exists)
output_dir = "sample_data_exports"
os.makedirs(output_dir, exist_ok=True)

# List and export each collection
collections = db.list_collection_names()

for coll_name in collections:
    data = list(db[coll_name].find())
    filename = os.path.join(output_dir, f"{coll_name}.json")
    
    with open(filename, "w") as f:
        f.write(dumps(data, indent=2))
    
    print(f"Exported {coll_name} → {filename}")


# In[114]:


from bson.json_util import dumps
import pandas as pd
import os


# In[115]:


# Output directory, this will export to JSON and CSV format.
output_dir = "sample_data_exports"
os.makedirs(output_dir, exist_ok=True)

# Collections to export
collections = db.list_collection_names()

for coll_name in collections:
    # Fetch data
    data = list(db[coll_name].find())

    # Export to JSON
    json_path = os.path.join(output_dir, f"{coll_name}.json")
    with open(json_path, "w") as f:
        f.write(dumps(data, indent=2))
    
    # Export to CSV (flattening embedded fields)
    try:
        df = pd.json_normalize(data)
        csv_path = os.path.join(output_dir, f"{coll_name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"✅ Exported {coll_name} to CSV and JSON.")
    except Exception as e:
        print(f"Could not export {coll_name} to CSV: {e}")


# In[118]:


#Check current indexes on the courses collection
for idx in db.courses.list_indexes():
    print(idx)


# In[119]:


#Bonus1; Text Search for Course Content
search_term = "data science"

results = db.courses.find({
    "$text": {
        "$search": search_term
    }
})

for course in results:
    print(f"{course['title']} - {course.get('description', '')}")


# In[121]:


#Bonus 3: Data archiving strategy for old enrollments
#A.This will look at enrolment  where completed is true, completeDate or enrolledAt is older than one year

from datetime import datetime, timedelta

cutoff_date = datetime.now() - timedelta(days=365)
criteria = {
    "completed": True,
    "completionDate": {"$lt": cutoff_date}
}



# In[ ]:


#Archive data (Move-and-delete Process)
# Step 1: Find old enrollments
old_enrollments = list(db.enrollments.find(criteria))

# Step 2: Insert into archive collection
if old_enrollments:
    db.enrollments_archive.insert_many(old_enrollments)

    # Step 3: Remove from active collection
    ids = [e["_id"] for e in old_enrollments]
    db.enrollments.delete_many({"_id": {"$in": ids}})

    print(f"✅ Archived {len(old_enrollments)} old enrollments.")
else:
    print("📂 No enrollments to archive.")

db.enrollments_archive.create_index("studentId")
db.enrollments_archive.create_index("courseId")
db.enrollments_archive.create_index("completionDate")


# In[127]:


get_ipython().system('jupyter nbconvert --to script eduhub.ipynb')


# In[ ]:




