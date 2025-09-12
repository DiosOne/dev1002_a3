-- query a single table
SELECT * FROM Books WHERE BookID = 1;

-- query joined tables
SELECT Loans.LoanID, Books.Title, Members.FirstName AS Borrower, Staff.FirstName AS StaffMember, Loans.LoanDate
FROM Loans
JOIN Books ON Loans.BookID = Books.BookID
JOIN Members ON Loans.MemberID = Members.MemberID
JOIN Staff ON Loans.StaffID = Staff.StaffID
WHERE Loans.LoanID = 1;
