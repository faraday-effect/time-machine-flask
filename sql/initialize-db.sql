INSERT INTO public.course (id, designation, name, semeser, year)
  VALUES (1, 'SYS 394', 'Information Systems Design', 'Spring', 2018);

INSERT INTO public.project (id, name, course_id)
  VALUES (1, 'Time Machine', 1);
INSERT INTO public.sprint (id, name, start_date, end_date, project_id)
  VALUES (1, 'Spring 1', '2018-03-12', '2018-03-23', 1);

INSERT INTO public.project (id, name, course_id)
  VALUES (2, 'Gardner''s Exchange', 1);

INSERT INTO public.team (id, name, project_id, course_id)
  VALUES (1, 'Team Nurk', 1, 1);
INSERT INTO public."user" (id, first_name, last_name, email, password)
  VALUES (1, 'Tom', 'Nurkkala', 'tnurkkala@cse.taylor.edu', 'password');
INSERT INTO public.user_team (user_id, team_id)
  VALUES (1, 1);

INSERT INTO public.time (id, description, project_id, user_id, start_date, start_time, end_date, end_time)
  VALUES (1, 'Define data model', 1, 1, '2018-03-12', '21:00:00', '2018-03-12', '22:33:00');
