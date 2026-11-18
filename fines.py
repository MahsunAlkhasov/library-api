from datetime import date

FINE_PER_DAY = 0.50


def days_late(due_date):
    return (date.today() - date.fromisoformat(due_date)).days


def fine_for(due_date):
    return max(0, days_late(due_date)) * FINE_PER_DAY


def current_loan_fine(loan):
    if loan["returned"] == 0:
        return fine_for(loan["due_date"])
    return loan["fine"]


def unpaid_loan_amount(loan):
    if loan["returned"] == 0:
        return fine_for(loan["due_date"])
    if loan["fine_paid"] == 0:
        return loan["fine"]
    return 0.0


def money(amount):
    return round(float(amount), 2)
