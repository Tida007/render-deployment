# Bincom SQL Test - FastAPI Project

A FastAPI application for displaying and managing Nigerian polling unit election results.

## Features

1. **Individual Polling Unit Results** - Display detailed results for a specific polling unit
2. **LGA Summary** - View summed total results for all polling units in a Local Government Area (with select box)
3. **Store Results** - Store/update results for all parties in a polling unit

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- SQL dump file from [Google Drive](https://drive.google.com/file/d/0B77xAtHK1hd4Ukx6SHpqTkd6TWM/view)

## Setup Instructions

### 1. Database Setup

#### Install MySQL
- Download and install MySQL Server from [mysql.com](https://dev.mysql.com/downloads/installer/)
- During installation:
  - Choose "Development Computer" configuration
  - Set a root password (remember this!)
  - Skip sample databases (sakila, world)

#### Create Database
The database `bincom_polling` should already be created. If not, run:
```powershell
python create_database.py
```

#### Import SQL Dump
1. Download the SQL dump file from the Google Drive link above
2. Save it to your project directory (e.g., `bincom_test.sql`)
3. Run the import script:
```powershell
python import_sql_dump.py "C:\path\to\bincom_test.sql"
```
Or if the file is in your Downloads folder:
```powershell
python import_sql_dump.py "$env:USERPROFILE\Downloads\bincom_test.sql"
```

### 2. Project Setup

#### Create and Activate Virtual Environment
```powershell
cd C:\Users\USER\fastapi-project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configure Database Connection
1. Copy `.env.example` to `.env` (or create `.env` manually)
2. Edit `.env` and replace `YOUR_PASSWORD` with your MySQL root password:
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/bincom_polling
```

### 3. Run the Application

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Usage

### Web Interface

- **Home Page**: `http://127.0.0.1:8000/`
  - Navigate to individual polling unit results
  - View LGA summaries with select box

- **Individual Polling Unit**: `http://127.0.0.1:8000/polling-unit/{id}`
  - Replace `{id}` with a polling unit ID (e.g., 1, 2, 3)
  - Displays all party results for that polling unit

- **LGA Summary**: `http://127.0.0.1:8000/lga-summary`
  - Select an LGA from the dropdown
  - View summed totals for all parties across all polling units in that LGA

### API Endpoints

- **API Documentation**: `http://127.0.0.1:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://127.0.0.1:8000/redoc` (ReDoc)

#### Key API Endpoints:

1. `GET /polling-units/{polling_unit_id}` - Get polling unit results
2. `GET /lgas/` - Get list of all LGAs
3. `GET /lgas/{lga_id}/summary` - Get LGA summary
4. `POST /polling-units/{polling_unit_id}/results` - Store polling unit results

Example: Store results for polling unit 1
```bash
curl -X POST "http://127.0.0.1:8000/polling-units/1/results" \
  -H "Content-Type: application/json" \
  -d '{
    "party_results": [
      {"party_abbreviation": "PDP", "party_score": 100},
      {"party_abbreviation": "APC", "party_score": 80}
    ],
    "entered_by_user": "admin"
  }'
```

## Project Structure

```
fastapi-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── routers/
│       ├── __init__.py
│       ├── polling_units.py # Polling unit endpoints
│       └── lgas.py          # LGA endpoints
├── templates/               # HTML templates
│   ├── index.html
│   ├── polling_unit.html
│   ├── lga_summary.html
│   └── error.html
├── create_database.py       # Database creation script
├── import_sql_dump.py       # SQL dump import script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create from .env.example)
└── README.md
```

## Database Schema

Key tables:
- `polling_unit` - Polling unit information
- `lga` - Local Government Area information
- `party` - Political parties
- `announced_pu_results` - Polling unit results
- `ward` - Ward information

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running: Check Windows Services
- Verify password in `.env` file matches MySQL root password
- Test connection: `mysql -u root -p`

### Import SQL Dump Issues
- Ensure the SQL file path is correct
- Check file encoding (should be UTF-8)
- Verify database exists before importing

### Port Already in Use
- Change port: `uvicorn app.main:app --reload --port 8001`
- Or stop the process using port 8000

## Development

### Adding New Features
- Models: Add to `app/models.py`
- Schemas: Add to `app/schemas.py`
- Routes: Add to `app/routers/` or `app/main.py`
- Templates: Add to `templates/`

## License

This project is for educational/testing purposes.
