INSERT INTO account (first_name, last_name, email, password_hash)
VALUES ('Admin', 'User', 'admin@example.com',
        'pbkdf2:sha256:50000$8TqukkDe$05da93f2d0fdd5ca7b4c671aa384ea633626903fbd5fcdd9bd0d8872bbd9d499')

INSERT INTO role (id, name) VALUES (1, 'Administrator');
INSERT INTO role (id, name) VALUES (2, 'Team Lead');
INSERT INTO role (id, name) VALUES (3, 'Team Member');

INSERT INTO account_role (account_id, role_id)
VALUES ((SELECT id
         FROM account
         WHERE email = 'admin@example.com'),
        (SELECT id
         FROM role
         WHERE name = 'Administrator'));

INSERT INTO public.semester (id, name, year) VALUES (1, 'Fall', 2017);
INSERT INTO public.semester (id, name, year) VALUES (2, 'Spring', 2018);