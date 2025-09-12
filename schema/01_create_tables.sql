-- authors table
CREATE TABLE Authors (
    AuthorID SERIAL PRIMARY KEY,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    Nationality VARCHAR(100)
);

-- books table
CREATE TABLE Books (
    BookID SERIAL PRIMARY KEY,
    Title VARCHAR(100) NOT NULL,
    ISBN VARCHAR(13) UNIQUE,
    Genre VARCHAR(100),
    YearPublished INT,
    AuthorID INT,
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)
        ON DELETE SET NULL
);

-- members table
CREATE TABLE Members (
    MemberID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    JoinDate DATE DEFAULT CURRENT_DATE
);

-- staff table
CREATE TABLE Staff (
    StaffID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Role VARCHAR(50),
    Email VARCHAR(100) UNIQUE
);

-- loans table
CREATE TABLE Loans (
    LoanID SERIAL PRIMARY KEY,
    BookID INT NOT NULL,
    MemberID INT NOT NULL,
    StaffID INT NOT NULL,
    LoanDate DATE DEFAULT CURRENT_DATE,
    DueDate DATE NOT NULL,
    ReturnDate DATE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
        ON DELETE CASCADE,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
        ON DELETE CASCADE,
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
        ON DELETE SET NULL
);
