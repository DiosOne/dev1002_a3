-- clear existing data and reset serial id's
TRUNCATE TABLE Loans, Books, Authors, Members, Staff RESTART IDENTITY CASCADE;

-- authors
INSERT INTO Authors (FirstName, LastName, Nationality) VALUES
('Terry', 'Pratchett', 'British'),
('Thomas', 'Harris', 'American'),
('William', 'Gibson', 'Canadian'),
('Matthew', 'Reilly', 'Australian'),
('Raymond E.', 'Feist', 'American');

-- books
INSERT INTO Books (Title, ISBN, Genre, YearPublished, AuthorID) VALUES
('Guards! Guards!', '9780552166669', 'Fantasy', 1989, 1),
('Hannibal', '9780099532941', 'Thriller', 1999, 2),
('Neuromancer', '9780441569595', 'Science Fiction', 1984, 3),
('Ice Station', '9780312981269', 'Action', 1998, 4),
('Magician', '9780007541570', 'Fantasy', 1982, 5);

-- members
INSERT INTO Members (FirstName, LastName, Email, JoinDate) VALUES
('Chris', 'Sheehan', 'c.sheehan@email.com', '2025-05-01'),
('Steve', 'Dave', 'stevedave@email.com', '2025-08-06'),
('Josh', 'Burrows', 'j.burrows@email.com', '2025-06-01');

-- staff
INSERT INTO Staff (FirstName, LastName, Role, Email) VALUES
('Clifford', 'Price', 'Manager', 'c.price@library.com'),
('Tony', 'Bourdain', 'Librarian', 't.bourdain@library.com');
