DROP TABLE IF EXISTS time;
DROP TABLE IF EXISTS account_team;
DROP TABLE IF EXISTS account_role;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS role;
DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS sprint;
DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS semester;

CREATE TABLE semester
(
  id   SERIAL      NOT NULL
    CONSTRAINT semester_pkey
    PRIMARY KEY,
  name VARCHAR(15) NOT NULL,
  year INTEGER     NOT NULL
);

CREATE TABLE course
(
  id          SERIAL      NOT NULL
    CONSTRAINT course_pkey
    PRIMARY KEY,
  designation VARCHAR(10) NOT NULL,
  name        VARCHAR(40) NOT NULL,
  semester_id  INTEGER     NOT NULL
    CONSTRAINT course_semester_id_fk
    REFERENCES semester
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

CREATE TABLE account
(
  id            SERIAL       NOT NULL
    CONSTRAINT user_pkey
    PRIMARY KEY,
  first_name    VARCHAR(40)  NOT NULL,
  last_name     VARCHAR(40)  NOT NULL,
  email         VARCHAR(80)  NOT NULL,
  password_hash VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX user_email_uindex
  ON account (email);

CREATE TABLE account_team
(
  account_id INTEGER NOT NULL
    CONSTRAINT user_team_user_id_fk
    REFERENCES account,
  team_id    INTEGER NOT NULL
    CONSTRAINT user_team_team_id_fk
    REFERENCES team,
  CONSTRAINT user_team_user_id_team_id_pk
  PRIMARY KEY (account_id, team_id)
);

CREATE TABLE time
(
  id          SERIAL       NOT NULL
    CONSTRAINT time_pkey
    PRIMARY KEY,
  description VARCHAR(100) NOT NULL,
  project_id  INTEGER      NOT NULL
    CONSTRAINT time_project_id_fk
    REFERENCES project,
  user_id     INTEGER      NOT NULL
    CONSTRAINT time_user_id_fk
    REFERENCES account,
  start_date  DATE         NOT NULL,
  start_time  TIME         NOT NULL,
  end_date    DATE         NOT NULL,
  end_time    TIME         NOT NULL
);

CREATE TABLE role
(
  id   SERIAL      NOT NULL
    CONSTRAINT role_pkey
    PRIMARY KEY,
  name VARCHAR(64) NOT NULL
);

CREATE UNIQUE INDEX role_name_uindex
  ON role (name);

CREATE TABLE account_role
(
  account_id INTEGER NOT NULL
    CONSTRAINT account_role_account_id_fk
    REFERENCES account,
  role_id    INTEGER NOT NULL
    CONSTRAINT account_role_role_id_fk
    REFERENCES role
);
