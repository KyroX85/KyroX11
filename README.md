# kyroX

KyroX is a simple AI assistant-style CLI app for business tracking.

## Features
- Track revenue and expenses
- Track operational tasks and mark completion
- View business dashboard (revenue, expense, profit)
- Get simple AI recommendations from current business status
- Auto-saves data to `business_data.json`

## Run
```bash
python3 KyroX.py
```

## Command format
Use `|` to separate values.

- `add revenue|category|amount|note`
- `add expense|category|amount|note`
- `add task|title|priority`
- `complete task|task_number`
- `dashboard`
- `tasks`
- `help`
- `exit`
