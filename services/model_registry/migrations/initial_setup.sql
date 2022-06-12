CREATE TABLE IF NOT EXISTS models (
  id serial PRIMARY KEY,
  model VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS model_history (
  id serial PRIMARY KEY,
  model_id int NOT NULL,
  version VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  git_repository VARCHAR(255) NOT NULL,
  commit_hash VARCHAR(255) NOT NULL,
  image VARCHAR(255) NOT NULL,
  data VARCHAR(255) NOT NULL,
  parameters JSON NOT NULL,
  FOREIGN KEY (model_id)
    REFERENCES models (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS model_history_model_id_version_uidx ON model_history (model_id, version);
CREATE INDEX IF NOT EXISTS model_history_model_id_idx ON model_history (model_id);
