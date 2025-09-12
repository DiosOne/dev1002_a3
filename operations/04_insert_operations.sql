-- add new member
INSERT INTO Members (FirstName, LastName, Email, JoinDate)
VALUES ('David', 'Green', 'd.green@email.com', DEFAULT);

-- add loan with FK data
INSERT INTO Loans (BookID, MemberID, StaffID, DueDate)
VALUES (2, 4, 2, '2025-08-10');