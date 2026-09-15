from collections import defaultdict
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Splitwisely API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Expense(BaseModel):
    id: int
    title: str
    category: Literal["Stay", "Food & drinks", "Transport", "Activities", "Other"]
    amount: float = Field(gt=0)
    paid_by: str
    split_between: list[str]
    day: str
    note: str = ""

class ExpenseCreate(BaseModel):
    title: str
    category: Literal["Stay", "Food & drinks", "Transport", "Activities", "Other"]
    amount: float = Field(gt=0)
    paid_by: str
    split_between: list[str]
    day: str
    note: str = ""

members = [
    {"name": "Aarav", "initials": "AR", "color": "#f4a261"},
    {"name": "Meera", "initials": "ME", "color": "#5b8e7d"},
    {"name": "Kabir", "initials": "KB", "color": "#e76f51"},
    {"name": "Priya", "initials": "PR", "color": "#8d6e9f"},
    {"name": "Rohan", "initials": "RO", "color": "#3a86ff"},
    {"name": "Nisha", "initials": "NI", "color": "#e9c46a"},
]

expenses = [
    Expense(id=1, title="Villa stay", category="Stay", amount=840.0, paid_by="Meera", split_between=[m["name"] for m in members], day="Day 1", note="4 nights near Candolim"),
    Expense(id=2, title="Airport cabs", category="Transport", amount=68.0, paid_by="Aarav", split_between=[m["name"] for m in members], day="Day 1", note="Both ways"),
        Expense(id=3, title="Dinner at Gunpowder", category="Food & drinks", amount=212.0, paid_by="Kabir", split_between=["Aarav", "Meera", "Kabir", "Rohan", "Nisha"], day="Day 2", note="Priya skipped beer"),
    Expense(id=4, title="Scuba diving", category="Activities", amount=320.0, paid_by="Rohan", split_between=["Aarav", "Meera", "Kabir", "Rohan"], day="Day 3", note="4 divers"),
    Expense(id=5, title="2am chai & snacks", category="Food & drinks", amount=24.0, paid_by="Nisha", split_between=["Aarav", "Nisha", "Priya"], day="Day 3", note="The important one"),
]

@app.get("/api/overview")
def overview():
    total = sum(e.amount for e in expenses)
    shares = calculate_balances()
    return {"members": members, "expenses": expenses, "total": total, "balances": shares, "settlements": calculate_settlements(shares)}

@app.post("/api/expenses", response_model=Expense)
def add_expense(payload: ExpenseCreate):
    validate_expense(payload)
    next_id = max((expense.id for expense in expenses), default=0) + 1
    expense = Expense(id=next_id, **payload.model_dump())
    expenses.insert(0, expense)
    return expense

@app.put("/api/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, payload: ExpenseCreate):
    validate_expense(payload)
    for index, expense in enumerate(expenses):
        if expense.id == expense_id:
            updated = Expense(id=expense_id, **payload.model_dump())
            expenses[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Expense not found")

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int):
    for index, expense in enumerate(expenses):
        if expense.id == expense_id:
            expenses.pop(index)
            return {"deleted": expense_id}
    raise HTTPException(status_code=404, detail="Expense not found")

def validate_expense(payload: ExpenseCreate):
    member_names = {member["name"] for member in members}
    if payload.paid_by not in member_names or not payload.split_between:
        raise HTTPException(status_code=422, detail="Choose a payer and at least one participant")
    if any(person not in member_names for person in payload.split_between):
        raise HTTPException(status_code=422, detail="Every participant must be a trip member")

def calculate_balances():
    paid = defaultdict(float)
    owed = defaultdict(float)
    for expense in expenses:
        paid[expense.paid_by] += expense.amount
        share = expense.amount / len(expense.split_between)
        for person in expense.split_between:
            owed[person] += share
    return [
        {"name": member["name"], "paid": round(paid[member["name"]], 2), "owed": round(owed[member["name"]], 2), "net": round(paid[member["name"]] - owed[member["name"]], 2)}
        for member in members
    ]

def calculate_settlements(balances):
    creditors = [[b["name"], b["net"]] for b in balances if b["net"] > 0.005]
    debtors = [[b["name"], -b["net"]] for b in balances if b["net"] < -0.005]
    creditors.sort(key=lambda item: item[1], reverse=True)
    debtors.sort(key=lambda item: item[1], reverse=True)
    result = []
    creditor_index = debtor_index = 0
    while creditor_index < len(creditors) and debtor_index < len(debtors):
        debtor, debt = debtors[debtor_index]
        creditor, credit = creditors[creditor_index]
        amount = round(min(debt, credit), 2)
        result.append({"from": debtor, "to": creditor, "amount": amount})
        debtors[debtor_index][1] -= amount
        creditors[creditor_index][1] -= amount
        if debtors[debtor_index][1] < 0.01:
            debtor_index += 1
        if creditors[creditor_index][1] < 0.01:
            creditor_index += 1
    return result
