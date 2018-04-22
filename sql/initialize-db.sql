INSERT INTO account (first_name, last_name, email, superuser, password_hash)
VALUES ('Admin', 'User', 'admin@example.com', TRUE,
        'pbkdf2:sha256:50000$8TqukkDe$05da93f2d0fdd5ca7b4c671aa384ea633626903fbd5fcdd9bd0d8872bbd9d499');

INSERT INTO public.role (name, is_default) VALUES ('Team Lead', false);
INSERT INTO public.role (name, is_default) VALUES ('Team Member', true);

INSERT INTO public.semester (id, name, year) VALUES (1, 'Fall', 2017);
INSERT INTO public.semester (id, name, year) VALUES (2, 'Spring', 2018);