# Petro-Canada D365 Sales Analytics

A Django application for importing Microsoft Dynamics 365 sales workbooks and analyzing category performance across multiple retail locations.

---

## Features

- Import D365 Excel sales workbooks
- Automatic category hierarchy creation
- Monthly trend analysis
- Store comparison dashboard
- Category drill-down navigation
- Opportunity analysis
- Interactive charts
- Gross margin, sales and unit analysis

---

## Technology

- Python 3.9
- Django 4.2
- OpenPyXL
- SQLite
- Chart.js

---

## Screenshots

(Add screenshots here)

---

## Installation

```bash
git clone https://github.com/paulfuther/petro_can_d365.git

cd petro_can_d365

python -m venv venv

source venv/bin/activate      # macOS/Linux

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate

python manage.py runserver
```

---

## Environment Variables

Create a `.env` file:

```
DJANGO_SECRET_KEY=your-secret-key
```

---

## Current Features

- Category hierarchy importer
- Workbook metadata extraction
- Trend analysis
- Drill-down navigation
- Opportunity analysis
- Responsive dashboard

---

## Planned Features

- SKU-level browser
- Product opportunity analysis
- Store ranking
- Export to Excel
- Executive dashboard
- Multi-year trend analysis

---

## License

MIT