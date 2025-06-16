EduHub MongoDB Backend

##Project Setup & Validation

EduHub is a backend database system for an online learning platform, implemented using MongoDB and PyMongo. To get started, clone the project, ensure MongoDB is running locally (`mongodb://localhost:27017`), and execute the Python setup scripts to create collections: `users`, `courses`, `enrollments`, `lessons`, `assignments`, and `submissions`. Each collection includes strong schema validation for required fields, proper data types, enumerated roles/statuses, and strict email format checks. Indexes were created for frequent queries on user emails, course titles/categories, assignment due dates, and enrollment lookups.

##Schema Overview & Querying

The schema is designed to support full educational workflows: instructors create courses and lessons, students enroll and submit assignments, and submissions are graded. CRUD operations cover real use cases like adding users, publishing courses, updating grades, and soft-deleting accounts. Query examples include active student lookups, instructor-course relationships, and searching courses by title. Aggregation pipelines were implemented to support analytics such as enrollment trends, course popularity, top-performing students, and instructor revenue.

##Performance Optimization & Challenges

Query performance was analyzed using the `.explain()` method and timed with Python’s `time` module. Indexing improved slow queries drastically—e.g., course search queries dropped from hundreds of milliseconds to <20ms. Challenges included maintaining referential integrity (e.g., submission `studentId` and `assignmentId` mappings), which was resolved through validation and careful data generation. Error handling was implemented for duplicate keys, missing fields, and invalid types to ensure resilience in data operations. The backend is now ready for production use in scalable e-learning environments.
