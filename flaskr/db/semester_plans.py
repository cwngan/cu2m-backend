from datetime import datetime

from bson import ObjectId
from pymongo.collection import ReturnDocument

from flaskr.db.database import get_db
from flaskr.db.models import SemesterPlan, SemesterPlanUpdate


def create_semester_plan(
    course_plan_id: ObjectId,
    semester: int,
    year: int,
):
    # Ensure the compound key (year, semester) does not exist in the database
    if get_semester_plan_by_attributes(
        course_plan_id=course_plan_id, semester=semester, year=year
    ):
        return None

    semester_plan = SemesterPlan(
        courses=[],
        semester=semester,
        year=year,
        course_plan_id=ObjectId(course_plan_id),
        created_at=datetime.now(),  # Set the created_at field
    )

    db = get_db().semester_plans
    result = db.insert_one(semester_plan.__dict__)
    semester_plan.id = result.inserted_id
    return semester_plan


def get_semester_plan(semester_plan_id: ObjectId):
    db = get_db().semester_plans
    doc = db.find_one({"_id": semester_plan_id})
    return SemesterPlan.model_validate(doc) if doc else None


def get_semester_plan_by_attributes(course_plan_id: ObjectId, semester: int, year: int):
    db = get_db().semester_plans
    doc = db.find_one(
        {"course_plan_id": course_plan_id, "semester": semester, "year": year}
    )
    return SemesterPlan.model_validate(doc) if doc else None


def update_semester_plan(semester_plan_id: ObjectId, updates: SemesterPlanUpdate):
    db = get_db().semester_plans
    doc = db.find_one_and_update(
        {"_id": semester_plan_id},
        {"$set": updates.model_dump(exclude_none=True)},
        return_document=ReturnDocument.AFTER,
    )
    return SemesterPlan.model_validate(doc) if doc else None


def delete_semester_plan(semester_plan_id: ObjectId):
    db = get_db().semester_plans
    doc = db.find_one_and_delete({"_id": semester_plan_id})
    return SemesterPlan.model_validate(doc) if doc else None


def get_semester_plans_by_course_plan(course_plan_id: ObjectId):
    db = get_db().semester_plans
    docs = db.find({"course_plan_id": course_plan_id})
    return [SemesterPlan.model_validate(doc) for doc in docs]
