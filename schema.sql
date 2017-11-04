CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(191) UNIQUE,
    INDEX index_name (name)
) CHARSET = utf8mb4;
CREATE TABLE problems (
    no INTEGER PRIMARY KEY,
    name VARCHAR(191) UNIQUE,
    INDEX index_name (name)
) CHARSET = utf8mb4;
CREATE TABLE submissions (
    id BIGINT PRIMARY KEY,
    problem_no INTEGER,
    user_id INTEGER,
    is_ac BOOLEAN,
    INDEX index_problem_no_user_id (problem_no, user_id)
) CHARSET = utf8mb4;
CREATE TABLE wikipages (
    name VARCHAR(191) PRIMARY KEY
) CHARSET = utf8mb4;

CREATE TABLE favorite_problems (
    user_id INTEGER,
    problem_no INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (problem_no) REFERENCES problems (no),
    PRIMARY KEY (user_id, problem_no)
) CHARSET = utf8mb4;
CREATE TABLE favorite_submissions (
    user_id INTEGER,
    submission_id BIGINT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (submission_id) REFERENCES submissions (id),
    PRIMARY KEY (user_id, submission_id)
) CHARSET = utf8mb4;
CREATE TABLE favorite_wikipages (
    user_id INTEGER,
    wikipage_name VARCHAR(191),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (wikipage_name) REFERENCES wikipages (name),
    PRIMARY KEY (user_id, wikipage_name)
) CHARSET = utf8mb4;
