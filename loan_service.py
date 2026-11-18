from datetime import date, timedelta

import book_repository
import checks
import fines
import loan_repository
import member_repository
import notifications
import validation
from errors import bad_request, conflict, not_found

DEFAULT_LOAN_DAYS = 14
RENEWAL_DAYS = 14


def list_loans(only_overdue):
    rows = loan_repository.list_loans()
    if only_overdue:
        return [loan for loan in rows if checks.is_loan_overdue(loan)]
    return rows


def get_loan(loan_id):
    loan = loan_repository.get_loan(loan_id)
    if loan is None:
        raise not_found("loan not found")
    return loan


def create_loan(data):
    if not data.get("book_id") or not data.get("member_id"):
        raise bad_request("book_id and member_id are required")
    if data.get("due_date") and not validation.is_valid_date(data["due_date"]):
        raise bad_request("invalid due_date")

    book = book_repository.get_book(data["book_id"])
    if book is None:
        raise not_found("book not found")
    member = member_repository.get_member(data["member_id"])
    if member is None:
        raise not_found("member not found")
    if not checks.is_book_available(book):
        raise conflict("book is not available")

    member_loans = loan_repository.list_loans_for_member(data["member_id"])
    owed = sum(fines.unpaid_loan_amount(loan) for loan in member_loans)
    if owed > 0:
        raise conflict("member has unpaid fines")

    open_loans = sum(1 for loan in member_loans if loan["returned"] == 0)
    if checks.has_reached_loan_limit(member, open_loans):
        raise conflict("loan limit reached")

    today = date.today()
    due_date = data.get("due_date") or (
        today + timedelta(days=DEFAULT_LOAN_DAYS)).isoformat()
    loan = loan_repository.create_loan(
        data["book_id"], data["member_id"], due_date, today.isoformat())
    book_repository.set_book_availability(data["book_id"], False)

    notifications.send_email(
        member["email"],
        "Book checked out",
        f"You checked out {book['title']}",
    )
    return loan


def return_book(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 1:
        raise conflict("loan already returned")

    fine = fines.fine_for(loan["due_date"])
    updated = loan_repository.mark_returned(loan_id, fine)
    book_repository.set_book_availability(loan["book_id"], True)

    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    notifications.send_email(
        member["email"],
        "Book returned",
        f"You returned {book['title']}. Fine: ${fines.money(fine)}",
    )
    return updated


def renew_loan(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 1:
        raise conflict("loan already returned")
    if checks.is_loan_overdue(loan):
        raise conflict("overdue loans cannot be renewed")
    if not checks.can_renew_loan(loan):
        raise conflict("loan was already renewed")

    new_due = (date.fromisoformat(
        loan["due_date"]) + timedelta(days=RENEWAL_DAYS)).isoformat()
    updated = loan_repository.extend_loan(loan_id, new_due)

    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    notifications.send_email(
        member["email"],
        "Loan renewed",
        f"You renewed {book['title']}",
    )
    return updated


def pay_fine(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 0:
        raise conflict("return the book before paying")
    if loan["fine"] <= 0 or loan["fine_paid"] == 1:
        raise conflict("no fine to pay")

    updated = loan_repository.mark_fine_paid(loan_id)
    member = member_repository.get_member(loan["member_id"])
    notifications.send_email(
        member["email"],
        "Fine paid",
        f"We received ${fines.money(loan['fine'])}",
    )
    return updated
