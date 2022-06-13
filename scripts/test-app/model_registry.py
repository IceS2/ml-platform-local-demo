import psycopg2
import psycopg2.extras

HOST = "localhost"
PORT = 5432
USER = "postgres"
PASSWORD = "password"
DATABASE = "registry"

INSERT_MODEL_TO_MODELS = """
INSERT INTO models (
    model
)
VALUES (
  %s
);
"""

INSERT_MODEL_TO_MODEL_HISTORY = """
INSERT INTO model_history (
    model_id,
    version,
    git_repository,
    commit_hash,
    image,
    data,
    parameters
)
VALUES (
  %s,
  %s,
  'dummy-repo',
  'dummy-commit',
  %s,
  'dummy-data',
  '{\"dummy\": \"params\"}'
);
"""

SELECT_GET_MODEL_ID = """
SELECT
    id
FROM models
WHERE model = '{model_name}'
"""

SELECT_MODEL_VERSION = """
SELECT
    image
FROM model_history
WHERE model_id = '{model_id}'
  AND version = '{version}'
"""


def insert_dummy_data(model_name: str, image: str, version: str):
    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD
    )
    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(INSERT_MODEL_TO_MODELS, (model_name,))
    cur.execute(SELECT_GET_MODEL_ID.format(model_name=model_name))
    model_id = cur.fetchone()["id"]
    cur.execute(INSERT_MODEL_TO_MODEL_HISTORY, (model_id, version, image))

    connection.commit()
    cur.close()
    connection.close()

def get_model_info(model_name: str, version: str) -> tuple:
    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD
    )
    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(SELECT_GET_MODEL_ID.format(model_name=model_name))
    model_id = cur.fetchone()["id"]

    cur.execute(SELECT_MODEL_VERSION.format(model_id=model_id, version=version))
    image = cur.fetchone()["image"]
    return model_id, image

