from datetime import datetime
from pymongo.collection import ReturnDocument
from bson import ObjectId

from flaskr.db.database import get_db
from flaskr.db.models import SemesterPlan


def create_semester_plan(
    course_plan_id: str,
    semester: int,
    year: int,
):
    semester_plan = SemesterPlan(
        courses=[],
        semester=semester,
        year=year,
        course_plan_id=ObjectId(course_plan_id),
        created_at=datetime.now(),  # Set the created_at field
    )

    db = get_db().semester_plans
    result = db.insert_one(semester_plan.model_dump(exclude_none=True))
    semester_plan.id = result.inserted_id
    return semester_plan


def get_semester_plan(semester_plan_id: str):
    db = get_db().semester_plans
    doc = db.find_one({"_id": ObjectId(semester_plan_id)})
    return SemesterPlan.model_validate(doc) if doc else None


def update_semester_plan(semester_plan_id: str, updates: dict):
    db = get_db().semester_plans
    # logger.debug(f"Updating semester plan {plan_id} with updates: {updates}")
    doc = db.find_one_and_update(
        {"_id": ObjectId(semester_plan_id)},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    # logger.debug(f"Updated document: {doc}")
    return SemesterPlan.model_validate(doc) if doc else None


def delete_semester_plan(semester_plan_id: str):
    db = get_db().semester_plans
    doc = db.find_one_and_delete({"_id": ObjectId(semester_plan_id)})
    return SemesterPlan.model_validate(doc) if doc else None


def get_semester_plans_by_course_plan(course_plan_id: str):
    db = get_db().semester_plans
    docs = db.find({"course_plan_id": ObjectId(course_plan_id)})
    return [SemesterPlan.model_validate(doc) for doc in docs]
