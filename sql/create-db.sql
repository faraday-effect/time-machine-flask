DROP TABLE IF EXISTS time;
DROP TABLE IF EXISTS user_team;
DROP TABLE IF EXISTS "user";
DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS sprint;
DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS course;

CREATE TABLE course
(
  id          SERIAL      NOT NULL
    CONSTRAINT course_pkey
    PRIMARY KEY,
  designation VARCHAR(10) NOT NULL,
  name        VARCHAR(40) NOT NULL,
  semeser     VARCHAR(10) NOT NULL,
  year        INTEGER     NOT NULL
);

CREATE TABLE project
(
  id        SERIAL       NOT NULL
    CONSTRAINT project_pkey
    PRIMARY KEY,
  name      VARCHAR(100) NOT NULL,
  course_id INTEGER      NOT NULL
    CONSTRAINT project_course_id_fk
    REFERENCES course
);

CREATE TABLE sprint
(
  id         SERIAL      NOT NULL
    CONSTRAINT sprint_pkey
    PRIMARY KEY,
  name       VARCHAR(40) NOT NULL,
  start_date DATE        NOT NULL,
  end_date   DATE        NOT NULL,
  project_id INTEGER     NOT NULL
    CONSTRAINT sprint_project_id_fk
    REFERENCES project
);

CREATE TABLE team
(
  id         SERIAL      NOT NULL
    CONSTRAINT team_pkey
    PRIMARY KEY,
  name       VARCHAR(40) NOT NULL,
  project_id INTEGER     NOT NULL
    CONSTRAINT team_project_id_fk
    REFERENCES project,
  course_id  INTEGER     NOT NULL
    CONSTRAINT team_course_id_fk
    REFERENCES course
);


CREATE TABLE "user"
(
  id         SERIAL      NOT NULL
    CONSTRAINT user_pkey
    PRIMARY KEY,
  first_name VARCHAR(40) NOT NULL,
  last_name  VARCHAR(40) NOT NULL,
  email      VARCHAR(80) NOT NULL
);

CREATE TABLE user_team
(
  user_id INTEGER NOT NULL
    CONSTRAINT user_team_user_id_fk
    REFERENCES "user",
  team_id INTEGER NOT NULL
    CONSTRAINT user_team_team_id_fk
    REFERENCES team,
  CONSTRAINT user_team_user_id_team_id_pk
  PRIMARY KEY (user_id, team_id)
);

CREATE TABLE time
(
  id          SERIAL       NOT NULL
    CONSTRAINT time_pkey
    PRIMARY KEY,
  description VARCHAR(100) NOT NULL,
  start_time  TIMESTAMP    NOT NULL,
  end_time    TIMESTAMP    NOT NULL,
  project_id  INTEGER      NOT NULL
    CONSTRAINT time_project_id_fk
    REFERENCES project,
  user_id     INTEGER      NOT NULL
    CONSTRAINT time_user_id_fk
    REFERENCES "user"
);
