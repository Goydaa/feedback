DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    email TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    priority TEXT DEFAULT 'Средний',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

INSERT INTO categories (name) VALUES 
('Учебный процесс и расписание'), 
('Хозяйственные и технические вопросы'), 
('Инфраструктура (Столовая / Общежитие)'),
('Внеучебная деятельность'),
('Другое (затрудняюсь выбрать)');