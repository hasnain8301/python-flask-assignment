from io import StringIO

import pandas as pd
from bson.objectid import ObjectId
from flask import Response, current_app, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from loguru import logger

from ..models.candidate_models import CandidateModel
from .utils import convert_objectid_to_str

candidate_namespace = Namespace("Candidate", description="Candidate related operations")

# Validator
candidate_model = candidate_namespace.model(
    "candidate",
    {
        "first_name": fields.String(required=True, description="first_name"),
        "last_name": fields.String(required=True, description="last_name"),
        "email": fields.String(required=True, description="email"),
    },
)


@candidate_namespace.route("/candidates")
class CandidateCRUD(Resource):
    @jwt_required()
    @candidate_namespace.doc(
        responses={200: "Success", 500: "Internal Server Error"},
        params={"Authorization": {"in": "header", "description": "Bearer token"}},
    )
    @candidate_namespace.expect(candidate_model)
    def post(self):
        candidate_data = request.json
        valid_candidate = CandidateModel(**candidate_data)
        current_app.db["candidates"].insert_one(
            valid_candidate.model_dump(by_alias=True)
        )
        logger.info(
            f"Created a new candidate profile in the candidate collection: {valid_candidate.model_dump(by_alias=True)}"
        )
        return valid_candidate.model_dump(by_alias=True, exclude="created_at"), 201


@candidate_namespace.route("/all-candidates")
@candidate_namespace.doc(
    params={
        "query": "Any keywrod like: Hasnain Nafees",
        "page": "example: 1",
        "per_page": "example: 10",
    }
)
class AllCandidate(Resource):
    @jwt_required()
    @candidate_namespace.doc(
        responses={200: "Success", 500: "Internal Server Error"},
        params={"Authorization": {"in": "header", "description": "Bearer token"}},
    )
    def get(self):
        query = request.args.get("query", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        search_filter = {
            "$or": [
                {"first_name": {"$regex": query, "$options": "i"}},
                {"last_name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
            ]
        }
        skip = (page - 1) * per_page
        cursor = (
            current_app.db["candidates"].find(search_filter).skip(skip).limit(per_page)
        )
        total_count = current_app.db["candidates"].count_documents(search_filter)
        candidates = [convert_objectid_to_str(doc) for doc in cursor]

        response = {
            "candidates": candidates,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page,
        }

        return response


@candidate_namespace.route("/candidates/<string:id>")
class CandidateOperations(Resource):
    @jwt_required()
    @candidate_namespace.doc(
        responses={200: "Success", 500: "Internal Server Error"},
        params={"Authorization": {"in": "header", "description": "Bearer token"}},
    )
    def get(self, id):
        candidate_data = current_app.db["candidates"].find_one({"_id": ObjectId(id)})
        if not candidate_model:
            return {"message": "Candidate not found"}, 404
        valid_candidate = CandidateModel(**candidate_data)
        return valid_candidate.model_dump(by_alias=True, exclude="created_at"), 200

    @jwt_required()
    @candidate_namespace.doc(
        responses={200: "Success", 500: "Internal Server Error"},
        params={"Authorization": {"in": "header", "description": "Bearer token"}},
    )
    @candidate_namespace.expect(candidate_model)
    def put(self, id):
        candidate_data = request.json
        valid_candidate = CandidateModel(**candidate_data)
        update_result = current_app.db["candidates"].update_one(
            {"_id": ObjectId(id)}, {"$set": valid_candidate.model_dump(by_alias=True)}
        )
        if update_result.matched_count == 0:
            return {"message": "Candidate not found"}, 404
        updated_candidate = current_app.db["candidates"].find_one({"_id": ObjectId(id)})
        valid_candidate_updated = CandidateModel(**updated_candidate)
        logger.info(
            f"Updated candidate profile in the candidate collection: {valid_candidate_updated.model_dump(by_alias=True)}"
        )
        return (
            valid_candidate_updated.model_dump(by_alias=True, exclude="created_at")
        ), 201

    @jwt_required()
    @candidate_namespace.doc(
        responses={200: "Success", 500: "Internal Server Error"},
        params={"Authorization": {"in": "header", "description": "Bearer token"}},
    )
    def delete(self, id):
        delete_result = current_app.db["candidates"].delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 0:
            return {"message": "Candidate not found"}, 404
        logger.info(f"Deleted candidate profile with id: {id}")
        return {"message": "Candidate deleted successfully"}, 200


@candidate_namespace.route("/generate-report")
class GenerateReport(Resource):
    @jwt_required()
    @candidate_namespace.doc(
        responses={200: "Success", 500: "Internal Server Error"},
        params={"Authorization": {"in": "header", "description": "Bearer token"}},
    )
    def get(self):
        try:
            candidates_data = current_app.db["candidates"].find()
            df = pd.DataFrame(candidates_data)
            df["_id"] = df["_id"].apply(lambda x: str(x))
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_output = csv_buffer.getvalue()
            return Response(
                csv_output,
                mimetype="text/csv",
                headers={
                    "Content-disposition": "attachment; filename=candidates_report.csv"
                },
            )
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            return {"error": "Internal Server Error"}, 500
