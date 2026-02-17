#!/usr/bin/env python3
"""
Pilot Surveys Seed Script
Creates two pilot survey templates with questions:
- Survey A: Rider Satisfaction (Trip Complete) - 10 questions
- Survey B: No-Show Cancellation Follow-Up - 8 questions
"""

import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import psycopg2

# DB config from env or defaults
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "pguser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "db")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )


# Survey A: Rider Satisfaction (Trip Complete) - 10 Questions
TEMPLATE_A = "Rider Satisfaction - Trip Complete"
QUESTIONS_A = [
    # 1
    {"text": "How satisfied are you overall with the microtransit service?", "criteria": "scale", "scales": 5, "parent_id": None, "ord": 1},
    # 2
    {"text": "How likely are you to recommend this service to a friend or neighbor?", "criteria": "scale", "scales": 10, "parent_id": None, "ord": 2},
    # 3
    {"text": "How satisfied are you with the timeliness of the service?", "criteria": "scale", "scales": 5, "parent_id": None, "ord": 3},
    # 4 - parent
    {"text": "Was your most recent ride on time?", "criteria": "categorical", "scales": None, "parent_id": None, "ord": 4, "categories": ["Yes", "No"]},
    # 4a - child of Q4, triggered by "No"
    {"text": "What caused the delay?", "criteria": "open", "scales": None, "parent_id": "PLACEHOLDER_Q4", "ord": 5, "parent_trigger": "No"},
    # 5
    {"text": "How would you rate the cleanliness and comfort of vehicles?", "criteria": "scale", "scales": 5, "parent_id": None, "ord": 6},
    # 6
    {"text": "How would you rate your experience with drivers?", "criteria": "scale", "scales": 5, "parent_id": None, "ord": 7},
    # 7
    {"text": "How has the microtransit service impacted your daily life?", "criteria": "open", "scales": None, "parent_id": None, "ord": 8},
    # 8
    {"text": "What improvements would you most like to see?", "criteria": "open", "scales": None, "parent_id": None, "ord": 9},
    # 9
    {"text": "Are there additional services or features you'd like?", "criteria": "open", "scales": None, "parent_id": None, "ord": 10},
    # 10
    {"text": "Would you like to share a memorable experience with the service?", "criteria": "open", "scales": None, "parent_id": None, "ord": 11},
]

# Survey B: No-Show Cancellation Follow-Up - 8 Questions
TEMPLATE_B = "No-Show Cancellation Follow-Up"
QUESTIONS_B = [
    # 1 - parent
    {"text": "Did you cancel the ride yourself?", "criteria": "categorical", "scales": None, "parent_id": None, "ord": 1, "categories": ["Yes", "No", "Don't recall"]},
    # 1a - child of Q1, triggered by "Yes"
    {"text": "What was the main reason for cancelling?", "criteria": "categorical", "scales": None, "parent_id": "PLACEHOLDER_Q1", "ord": 2, "parent_trigger": "Yes",
     "categories": ["Found alternative transport", "No longer needed the ride", "Wait time too long", "App/booking issues", "Other"]},
    # 1b - child of Q1, triggered by "No"
    {"text": "Can you describe what happened with your ride?", "criteria": "open", "scales": None, "parent_id": "PLACEHOLDER_Q1", "ord": 3, "parent_trigger": "No"},
    # 2
    {"text": "How satisfied are you with communication about your ride status?", "criteria": "scale", "scales": 5, "parent_id": None, "ord": 4},
    # 3
    {"text": "Was the estimated arrival time accurate?", "criteria": "categorical", "scales": None, "parent_id": None, "ord": 5, "categories": ["Yes", "No", "Didn't receive one"]},
    # 4
    {"text": "How likely are you to use the service again?", "criteria": "scale", "scales": 10, "parent_id": None, "ord": 6},
    # 5
    {"text": "What would make you more likely to complete future rides?", "criteria": "open", "scales": None, "parent_id": None, "ord": 7},
    # 6
    {"text": "Any additional feedback you'd like to share?", "criteria": "open", "scales": None, "parent_id": None, "ord": 8},
]


def seed_template(conn, template_name: str, questions_spec: list):
    cur = conn.cursor()

    # Check if template already exists (idempotent)
    cur.execute("SELECT name FROM templates WHERE name = %s", (template_name,))
    if cur.fetchone():
        print(f"  Template '{template_name}' already exists, skipping.")
        return

    print(f"  Creating template: {template_name}")
    now = datetime.now(timezone.utc).isoformat()[:19].replace("T", " ")
    cur.execute(
        "INSERT INTO templates (name, created_at, status) VALUES (%s, %s, 'Published')",
        (template_name, now),
    )

    # Build questions with IDs; track parent placeholders
    q_ids = {}
    questions_to_insert = []
    categories_to_insert = []
    mappings_to_insert = []

    for i, q in enumerate(questions_spec):
        qid = str(uuid4())
        q_ids[i] = qid
        if q.get("parent_id") and q["parent_id"].startswith("PLACEHOLDER_"):
            # Will resolve after we have parent IDs
            pass
        questions_to_insert.append((
            qid,
            q["text"],
            q["criteria"],
            q.get("scales"),
            None,  # parent_id - set later
            "No",
        ))

    # Resolve parent IDs
    parent_placeholders = {}
    for i, q in enumerate(questions_spec):
        if q.get("parent_id") == "PLACEHOLDER_Q4":
            parent_placeholders[i] = 3  # Q4 is index 3 in Survey A
        elif q.get("parent_id") == "PLACEHOLDER_Q1":
            parent_placeholders[i] = 0  # Q1 is index 0 in Survey B

    for i, row in enumerate(questions_to_insert):
        q = questions_spec[i]
        parent_idx = parent_placeholders.get(i)
        parent_id = q_ids.get(parent_idx) if parent_idx is not None else None
        # Update the row's parent_id
        questions_to_insert[i] = (row[0], row[1], row[2], row[3], parent_id, row[5])

    # Insert questions
    for row in questions_to_insert:
        cur.execute(
            "INSERT INTO questions (id, text, criteria, scales, parent_id, autofill) VALUES (%s, %s, %s, %s, %s, %s)",
            row,
        )

    # Insert categories for categorical questions and mappings for children
    for i, q in enumerate(questions_spec):
        qid = q_ids[i]
        if q.get("criteria") == "categorical" and q.get("categories"):
            for cat_text in q["categories"]:
                cat_id = str(uuid4())
                cur.execute(
                    "INSERT INTO question_categories (id, question_id, text) VALUES (%s, %s, %s)",
                    (cat_id, qid, cat_text),
                )
                # If this is a parent and we have a child with parent_trigger, store for mapping
                for j, cq in enumerate(questions_spec):
                    if cq.get("parent_id") and str(parent_placeholders.get(j)) == str(i) and cq.get("parent_trigger") == cat_text:
                        mappings_to_insert.append((q_ids[j], cat_id))

    # Insert question_category_mappings for child questions
    for child_id, parent_cat_id in mappings_to_insert:
        cur.execute(
            "INSERT INTO question_category_mappings (child_question_id, parent_category_id) VALUES (%s, %s)",
            (child_id, parent_cat_id),
        )

    # Insert template_questions
    for i, q in enumerate(questions_spec):
        cur.execute(
            "INSERT INTO template_questions (template_name, question_id, ord) VALUES (%s, %s, %s)",
            (template_name, q_ids[i], q["ord"]),
        )

    conn.commit()
    print(f"  Created {len(questions_spec)} questions for '{template_name}'")


def main():
    print("Pilot Surveys Seed Script")
    print("=" * 50)

    try:
        conn = get_conn()
        print("Connected to database.")
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    try:
        print("\nSeeding Survey A: Rider Satisfaction (Trip Complete)...")
        seed_template(conn, TEMPLATE_A, QUESTIONS_A)

        print("\nSeeding Survey B: No-Show Cancellation Follow-Up...")
        seed_template(conn, TEMPLATE_B, QUESTIONS_B)

        print("\nDone. Both pilot templates are Published.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
