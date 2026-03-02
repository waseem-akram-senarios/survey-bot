"""
Template-question association endpoints for the Template Service.
"""

from fastapi import APIRouter, Body, HTTPException

from shared.models.common import (
    GetTemplateQuestionsRequestP,
    TemplateQuestionCreateP,
    TemplateQuestionDeleteRequestP,
)

from db import process_question_stats, sql_execute

router = APIRouter()


@router.post(
    "/templates/addquestions",
    status_code=201,
    description="Add question to template (check template exists, check question exists, insert into template_questions).",
)
async def add_question_to_template(template_question: TemplateQuestionCreateP):
    try:
        res = sql_execute(
            "SELECT * FROM templates WHERE name = :template_name",
            {"template_name": template_question.TemplateName},
        )
        if not res:
            raise HTTPException(
                status_code=404,
                detail=f"Template with Name {template_question.TemplateName} not found",
            )

        question_response = sql_execute(
            "SELECT * FROM questions WHERE id = :question_id",
            {"question_id": template_question.QueId},
        )
        if not question_response:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID {template_question.QueId} not found",
            )

        sql_execute(
            "INSERT INTO template_questions (template_name, ord, question_id) VALUES (:template_name, :ord, :question_id)",
            {
                "template_name": template_question.TemplateName,
                "ord": template_question.Order,
                "question_id": template_question.QueId,
            },
        )
        return {
            "message": f"Question with Id {template_question.QueId} added to template {template_question.TemplateName} successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/templates/getquestions",
    description="Get all questions for a template (complex JOIN query with categories, parent_category_texts, ordered by ord).",
)
async def get_template_questions(request: GetTemplateQuestionsRequestP):
    template_name = request.TemplateName
    try:
        res = sql_execute(
            "SELECT * FROM templates WHERE name = :template_name",
            {"template_name": template_name},
        )
        if not res:
            raise HTTPException(
                status_code=404,
                detail=f"Template with Name {template_name} not found",
            )

        questions = sql_execute(
            """SELECT
  q.id,
  q.text,
  q.criteria,
  q.scales,
  q.parent_id,
  q.autofill,
  tq.ord,
  COALESCE(array_agg(qc.text ORDER BY qc.id) FILTER (WHERE qc.text IS NOT NULL), '{}') AS categories,
  COALESCE(pm.parent_category_texts, '{}') AS parent_category_texts
FROM template_questions tq
JOIN questions q ON tq.question_id = q.id
LEFT JOIN question_categories qc ON q.id = qc.question_id
LEFT JOIN (
  SELECT m.child_question_id,
         array_agg(qc2.text ORDER BY qc2.id) AS parent_category_texts
  FROM question_category_mappings m
  JOIN question_categories qc2 ON qc2.id = m.parent_category_id
  GROUP BY m.child_question_id
) pm ON pm.child_question_id = q.id
WHERE tq.template_name = :template_name
GROUP BY q.id, q.text, q.criteria, q.scales, q.parent_id, q.autofill, tq.ord, pm.parent_category_texts
ORDER BY tq.ord""",
            {"template_name": template_name},
        )

        return {"TemplateName": template_name, "Questions": questions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/templates/deletequestionbyidwithparentchild",
    description="Delete question from template including parent/child relationships.",
)
async def delete_template_question_fromid_with_parent_child(
    request: TemplateQuestionDeleteRequestP = Body(...),
):
    try:
        template_name = request.TemplateName
        queid = request.QueId

        sql_execute(
            """DELETE FROM question_categories
            WHERE question_id = :question_id
            OR question_id IN (SELECT id FROM questions WHERE parent_id = :question_id)""",
            {"question_id": queid},
        )

        sql_execute(
            """DELETE FROM template_questions
            WHERE question_id = :question_id
            OR question_id IN (SELECT id FROM questions WHERE parent_id = :question_id)""",
            {"question_id": queid},
        )

        sql_execute(
            "DELETE FROM questions WHERE parent_id = :question_id",
            {"question_id": queid},
        )

        sql_execute(
            "DELETE FROM questions WHERE id = :question_id",
            {"question_id": queid},
        )

        return {
            "message": f"Question with ID '{queid}' deleted from template '{template_name}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/templates/getqna",
    description="Get questions with aggregated answers and statistics for completed surveys.",
)
async def get_template_answers(request: GetTemplateQuestionsRequestP):
    template_name = request.TemplateName
    try:
        res = sql_execute(
            "SELECT * FROM templates WHERE name = :template_name",
            {"template_name": template_name},
        )
        if not res:
            raise HTTPException(
                status_code=404,
                detail=f"Template with Name {template_name} not found",
            )

        question_texts = sql_execute(
            """SELECT
  q.id AS question_id,
  q.text AS question_text,
  q.criteria,
  q.scales,
  q.parent_id,
  q.autofill,
  COALESCE(MAX(qc.categories::text)::json, '[]') AS categories,
  json_agg(sri.answer ORDER BY sri.answer) AS answers
FROM survey_response_items sri
JOIN questions q ON sri.question_id = q.id
LEFT JOIN (
  SELECT question_id, json_agg(text ORDER BY CASE WHEN lower(text) = 'none of the above' THEN 1 ELSE 0 END, text) AS categories
  FROM question_categories
  GROUP BY question_id
) qc ON qc.question_id = q.id
JOIN surveys s ON s.id = sri.survey_id
WHERE s.template_name = :template_name
  AND s.status = 'Completed'
  AND sri.answer IS NOT NULL
GROUP BY q.id, q.text, q.criteria, q.scales, q.parent_id, q.autofill
ORDER BY q.id""",
            {"template_name": template_name},
        )

        dict_results = [dict(row) for row in question_texts]
        for question in dict_results:
            question["Stats"] = process_question_stats(question)

        return dict_results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
