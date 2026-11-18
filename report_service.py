import book_repository
import fines
import loan_repository
import report_repository


def overdue_report():
    rows = report_repository.list_open_loans_with_details()
    items = []
    total = 0.0
    for r in rows:
        late = fines.days_late(r["due_date"])
        if late > 0:
            fine = fines.fine_for(r["due_date"])
            total += fine
            items.append(
                {
                    "loan_id": r["id"],
                    "title": r["title"],
                    "member": r["name"],
                    "days_late": late,
                    "fine": fines.money(fine),
                }
            )
    return {"items": items, "total_fines": fines.money(total)}


def summary_report():
    total_books = book_repository.count_books()
    loans = loan_repository.list_loans()
    on_loan = sum(1 for loan in loans if loan["returned"] == 0)
    outstanding = sum(fines.unpaid_loan_amount(loan) for loan in loans)
    return {
        "total_books": total_books,
        "on_loan": on_loan,
        "fines_outstanding": fines.money(outstanding),
    }
