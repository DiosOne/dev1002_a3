-- update a books genre
UPDATE Books
SET Genre = 'Classic Fantasy'
WHERE BookID = 1;

-- delete a member and cascade their loans
DELETE FROM Members
WHERE MemberID = 4;