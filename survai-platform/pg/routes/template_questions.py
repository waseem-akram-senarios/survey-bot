from fastapi import APIRouter, HTTPException
from models import (
    GetTemplateQuestionsRequestP,
    TemplateQuestionCreateP,
    TemplateQuestionDeleteRequestP,
)
from utils import process_question_stats, sql_execute

router = APIRouter()


@router.post(
    "/templates/addquestions",
    status_code=201,
    description="""
    Associate an existing question with a template in a specific order.
    
    Args:
        template_question (object): Object containing:
            - TemplateName (str): Name of the template
            - QueId (str): ID of the question to add
            - Order (int): Position order of the question in the template
    
    Returns:
        dict: Object containing:
            - message (str): Success confirmation message
    """,
)
async def add_question_to_template(template_question: TemplateQuestionCreateP):
    try:
        # Check if template exists
        sql_query = """SELECT * FROM templates WHERE name = :template_name"""
        sql_dict = {"template_name": template_question.TemplateName}
        res = sql_execute(sql_query, sql_dict)
        if not res:
            raise HTTPException(
                status_code=404,
                detail=f"Template with Name {template_question.TemplateName} not found",
            )

        # Check if question exists
        sql_query = """SELECT * FROM questions WHERE id = :question_id"""
        sql_dict = {"question_id": template_question.QueId}
        question_response = sql_execute(sql_query, sql_dict)
        if not question_response:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID {template_question.QueId} not found",
            )

        # Create item for TemplateQuestions table
        sql_query = """INSERT INTO template_questions (template_name, ord, question_id)
VALUES (:template_name, :ord, :question_id)"""
        sql_dict = {
            "template_name": template_question.TemplateName,
            "ord": template_question.Order,
            "question_id": template_question.QueId,
        }
        sql_execute(sql_query, sql_dict)

        return {
            "message": f"Question with Id {template_question.QueId} added to template {template_question.TemplateName} successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/templates/getquestions",
    description="""
    Retrieve all questions associated with a template in order.
    
    Args:
        request (object): Object containing:
            - TemplateName (str): Name of the template
    
    Returns:
        dict: Object containing:
            - TemplateName (str): Template name
            - Questions (list): Array of question objects, each containing:
                - id (str): Question ID
                - text (str): Question text
                - criteria (str): Question type
                - scales (int | None): Scale value
                - parent_id (str | None): Parent question ID
                - ord (int): Question order in template
                - categories (list): Question categories
                - autofill (str): Whether to autofill the question
    """,
)
async def get_template_questions(request: GetTemplateQuestionsRequestP):
    template_name = request.TemplateName
    try:
        # Check if template exists
        sql_query = """SELECT * FROM templates WHERE name = :template_name"""
        sql_dict = {"template_name": request.TemplateName}
        res = sql_execute(sql_query, sql_dict)
        if not res:
            raise HTTPException(
                status_code=404,
                detail=f"Template with Name {request.TemplateName} not found",
            )

        sql_query = """SELECT 
  q.id,
  q.text,
  q.criteria,
  q.scales,
  q.parent_id,
  q.autofill,
  tq.ord,
  COALESCE(array_agg(qc.text ORDER BY qc.id) 
           FILTER (WHERE qc.text IS NOT NULL), '{}') AS categories,
  COALESCE(pm.parent_category_texts, '{}') AS parent_category_texts
FROM 
  template_questions tq
JOIN 
  questions q ON tq.question_id = q.id
LEFT JOIN 
  question_categories qc ON q.id = qc.question_id
LEFT JOIN (
  SELECT m.child_question_id,
         array_agg(qc2.text ORDER BY qc2.id) AS parent_category_texts
    FROM question_category_mappings m
    JOIN question_categories qc2 ON qc2.id = m.parent_category_id
   GROUP BY m.child_question_id
) pm ON pm.child_question_id = q.id
WHERE 
  tq.template_name = :template_name
GROUP BY 
  q.id, q.text, q.criteria, q.scales, q.parent_id, q.autofill, tq.ord, pm.parent_category_texts
ORDER BY 
  tq.ord;"""
        sql_dict = {"template_name": request.TemplateName}
        questions = sql_execute(sql_query, sql_dict)

        return {
            "TemplateName": template_name,
            "Questions": questions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.put("/templates/editquestions")
# async def edit_template_question(template_question: TemplateQuestionCreate):
#     No need since it can be done via the @router.patch("/questions" route


# @router.delete("/templates/deletequestionbyid")
# async def delete_template_question_fromid(request: TemplateQuestionDeleteRequestP):
# replaced with delete_template_question_fromid_with_parent_child


@router.delete(
    "/templates/deletequestionbyidwithparentchild",
    description="""
    Remove a question from a template and delete the question along with any parent/child relationships.
    
    Args:
        request (object): Object containing:
            - TemplateName (str): Name of the template
            - QueId (str): ID of the question to delete
    
    Returns:
        dict: Object containing:
            - message (str): Success confirmation message
    """,
)
async def delete_template_question_fromid_with_parent_child(
    request: TemplateQuestionDeleteRequestP,
):
    try:
        template_name = request.TemplateName
        queid = request.QueId

        # delete category‐choices for question and for its children
        sql_query = """DELETE FROM question_categories
 WHERE question_id = :question_id
    OR question_id IN (
         SELECT id
           FROM questions
          WHERE parent_id = :question_id
       )"""
        sql_dict = {"question_id": queid}
        _ = sql_execute(sql_query, sql_dict)

        # delete template_questions for question and for its children
        sql_query = """DELETE FROM template_questions
 WHERE question_id = :question_id
    OR question_id IN (
         SELECT id
           FROM questions
          WHERE parent_id = :question_id
       )"""
        sql_dict = {"question_id": queid}
        _ = sql_execute(sql_query, sql_dict)

        # delete child questions
        sql_query = """DELETE FROM questions
 WHERE parent_id = :question_id"""
        sql_dict = {"question_id": queid}
        _ = sql_execute(sql_query, sql_dict)

        # delete question itself
        sql_query = """DELETE FROM questions
 WHERE id = :question_id"""
        sql_dict = {"question_id": queid}
        _ = sql_execute(sql_query, sql_dict)

        return {
            "message": f"Question with ID '{queid}' deleted from template '{template_name}'"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/templates/getqna",
    description="""
    Get questions and their aggregated answers/statistics for a template.
    
    Args:
        request (object): Object containing:
            - TemplateName (str): Name of the template
    
    Returns:
        list: Array of question objects with answers, each containing:
            - question_id (str): Question ID
            - question_text (str): Question text
            - criteria (str): Question type
            - scales (int | None): Scale value
            - parent_id (str | None): Parent question ID
            - categories (list): Question categories
            - answers (list): All submitted answers
            - Stats (dict): Statistical analysis of answers
            - autofill (str): Whether to autofill the question
    """,
)
async def get_template_answers(request: GetTemplateQuestionsRequestP):
    template_name = request.TemplateName
    try:
        # Check if template exists
        sql_query = """SELECT * FROM templates WHERE name = :template_name"""
        sql_dict = {"template_name": request.TemplateName}
        res = sql_execute(sql_query, sql_dict)
        if not res:
            raise HTTPException(
                status_code=404,
                detail=f"Template with Name {request.TemplateName} not found",
            )

        sql_query = """SELECT
  q.id AS question_id,
  q.text AS question_text,
  q.criteria,
  q.scales,
  q.parent_id,
  q.autofill,
  COALESCE(
    MAX(qc.categories::text)::json,
    '[]'
  ) AS categories,
  json_agg(sri.answer ORDER BY sri.answer) AS answers
FROM survey_response_items sri
JOIN questions q
  ON sri.question_id = q.id
LEFT JOIN (
  SELECT
    question_id,
    json_agg(text ORDER BY CASE WHEN lower(text) = 'none of the above' THEN 1 ELSE 0 END, text) AS categories
  FROM question_categories
  GROUP BY question_id
) qc
  ON qc.question_id = q.id
JOIN surveys s
  ON s.id = sri.survey_id
WHERE s.template_name = :template_name
  AND s.status = 'Completed'
  AND sri.answer IS NOT NULL
GROUP BY q.id, q.text, q.criteria, q.scales, q.parent_id, q.autofill
ORDER BY q.id;"""
        sql_dict = {"template_name": template_name}
        question_texts = sql_execute(sql_query, sql_dict)
        dict_results = [dict(row) for row in question_texts]

        for question in dict_results:
            question["Stats"] = process_question_stats(question)

        return dict_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
