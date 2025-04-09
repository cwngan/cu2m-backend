from datetime import datetime, timezone
from bson import ObjectId
from pymongo import ReturnDocument
from flaskr.db.database import get_db
from flaskr.db.models import CoursePlan, CoursePlanUpdate


def get_course_plan(course_plan_id: ObjectId) -> CoursePlan | None:
    """
    Return CoursePlan of specified ID.

    :param course_plan_id: the ID of the target CoursePlan.
    :return: the CoursePlan object or None if not found.
    """
    course_plans_collection = get_db().course_plans
    doc = course_plans_collection.find_one({"_id": course_plan_id})
    return CoursePlan.model_validate(doc) if doc else None


def create_course_plan(
    description: str, name: str, user_id: ObjectId
) -> CoursePlan | None:
    """
    Create and insert into database a CoursePlan document with given parameters.

    :param description: the description of the course plan.
    :param name: the name of the course plan.
    :param user_id: the ObjectID of the user who created the course plan.
    :return: the created CoursePlan object or None if not created.
    """
    course_plans_collection = get_db().course_plans
    course_plan = CoursePlan(
        description=description,
        name=name,
        user_id=None,
        updated_at=datetime.now(tz=timezone.utc),
        favourite=False,
    )
    data = course_plan.model_dump(exclude_none=True)
    # model_dump converts bson.ObjectId to string
    # so we have to first insert the CoursePlan
    # and update user_id correctly
    course_plan_id = course_plans_collection.insert_one(data).inserted_id
    doc = course_plans_collection.find_one_and_update(
        {"_id": course_plan_id},
        {"$set": {"user_id": user_id}},
        return_document=ReturnDocument.AFTER,
    )
    return CoursePlan.model_validate(doc) if doc else None


def update_course_plan(
    course_plan_id: ObjectId, course_plan_update: CoursePlanUpdate
) -> CoursePlan | None:
    """
    Update CoursePlan of specified ID with given update parameters.

    :param course_plan_id: the ID of the target CoursePlan.
    :param course_plan_update: the CoursePlanUpdate object that contains data for update.
    :return: the updated CoursePlan object or None if not found.
    """
    course_plans_collection = get_db().course_plans
    data = course_plan_update.model_dump(exclude_none=True)
    doc = course_plans_collection.find_one_and_update(
        {"_id": course_plan_id}, {"$set": data}, return_document=ReturnDocument.AFTER
    )
    return CoursePlan.model_validate(doc) if doc else None


def delete_course_plan(course_plan_id: ObjectId) -> CoursePlan:
    """
    Delete CoursePlan of specified ID.

    :param course_plan_id: the ID of the target CoursePlan.
    :return: the deleted CoursePlan object or None if not found.
    """
    course_plans_collection = get_db().course_plans
    course_plan = course_plans_collection.find_one({"_id": course_plan_id})
    if course_plan:
        doc = course_plans_collection.find_one_and_delete({"_id": course_plan_id})
        return CoursePlan.model_validate(doc) if doc else None
    return None
