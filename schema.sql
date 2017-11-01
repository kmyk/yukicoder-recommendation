PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE INDEX index_name ON users (name);
CREATE TABLE problems (
    no INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY,
    problem_no INTEGER NOT NULL,
    user_id INTEGER NOT NULL
);
CREATE INDEX index_user_id ON submissions (user_id);
CREATE TABLE wikipages (
    name TEXT PRIMARY KEY
);

CREATE TABLE favorite_problems (
    user_id INTEGER,
    problem_no INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (problem_no) REFERENCES problems (no),
    PRIMARY KEY (user_id, problem_no)
);
CREATE TABLE favorite_submissions (
    user_id INTEGER,
    submission_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (submission_id) REFERENCES submissions (id),
    PRIMARY KEY (user_id, submission_id)
);
CREATE TABLE favorite_wikipages (
    user_id INTEGER,
    wikipage_name TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (wikipage_name) REFERENCES wikipages (name),
    PRIMARY KEY (user_id, wikipage_name)
);
