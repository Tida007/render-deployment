from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.routers import polling_units, lgas
from app.models import LGA

app = FastAPI(title="Bincom SQL Test", version="0.1.0")

# Include routers
app.include_router(polling_units.router)
app.include_router(lgas.router)

# Setup templates
templates = Environment(loader=FileSystemLoader("templates"))


@app.get("/", response_class=HTMLResponse, tags=["root"])
def read_root(request: Request):
    """Home page with navigation"""
    template = templates.get_template("index.html")
    return HTMLResponse(content=template.render(request=request))


@app.get("/polling-unit/{polling_unit_id}", response_class=HTMLResponse, tags=["frontend"])
def polling_unit_page(polling_unit_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Feature 1: Display individual polling unit results on a web page
    """
    from app.routers.polling_units import get_polling_unit_results
    
    try:
        result = get_polling_unit_results(polling_unit_id, db)
        template = templates.get_template("polling_unit.html")
        return HTMLResponse(content=template.render(
            request=request,
            polling_unit=result,
            polling_unit_id=polling_unit_id
        ))
    except Exception as e:
        template = templates.get_template("error.html")
        return HTMLResponse(content=template.render(
            request=request,
            error_message=str(e)
        ))


@app.get("/lga-summary", response_class=HTMLResponse, tags=["frontend"])
def lga_summary_page(request: Request, db: Session = Depends(get_db)):
    """
    Feature 2: Display LGA summary with select box
    """
    try:
        lgas_list = db.query(LGA).order_by(LGA.lga_name).all()
        template = templates.get_template("lga_summary.html")
        return HTMLResponse(content=template.render(
            request=request,
            lgas=lgas_list
        ))
    except Exception as e:
        template = templates.get_template("error.html")
        return HTMLResponse(content=template.render(
            request=request,
            error_message=f"Database error: {str(e)}"
        ), status_code=500)


@app.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that also tests database connection"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }


