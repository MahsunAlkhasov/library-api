from datetime import date

STUDENT_LOAN_LIMIT = 3
STAFF_LOAN_LIMIT = 5


def is_book_available(book):
    return bool(book["available"])


def is_loan_overdue(loan):
    return loan["returned"] == 0 and date.fromisoformat(loan["due_date"]) < date.today()


def can_renew_loan(loan):
    return loan["returned"] == 0 and not is_loan_overdue(loan) and loan["renewals"] < 1


def member_loan_limit(member):
    return STAFF_LOAN_LIMIT if member["type"] == "staff" else STUDENT_LOAN_LIMIT


def has_reached_loan_limit(member, open_loans_count):
    return open_loans_count >= member_loan_limit(member)
