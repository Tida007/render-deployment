"""Router for LGA endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import LGA, PollingUnit, AnnouncedPUResult
from app.schemas import LGASummary, LGAInfo, PartyResult

router = APIRouter(prefix="/lgas", tags=["lgas"])


@router.get("/", response_model=List[LGAInfo])
def get_all_lgas(db: Session = Depends(get_db)):
    """
    Get list of all LGAs for select box
    
    Used for Feature 2: LGA selection
    """
    try:
        lgas = db.query(LGA).order_by(LGA.lga_name).all()
        
        return [
            LGAInfo(lga_id=lga.lga_id, lga_name=lga.lga_name)
            for lga in lgas
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )


@router.get("/{lga_id}/summary", response_model=LGASummary)
def get_lga_summary(lga_id: int, db: Session = Depends(get_db)):
    """
    Get summed total results for all polling units in an LGA
    
    Feature 2: Display summed total result of all polling units under a particular LGA
    
    IMPORTANT: This calculates the sum from announced_pu_results (polling unit results),
    NOT from announced_lga_results table. The announced_lga_results table is for
    comparison purposes only.
    """
    try:
        # Get LGA info
        lga = db.query(LGA).filter(LGA.lga_id == lga_id).first()
        
        if not lga:
            raise HTTPException(status_code=404, detail="LGA not found")
        
        # Get all polling units in this LGA
        polling_units = db.query(PollingUnit).filter(
            PollingUnit.lga_id == lga_id
        ).all()
        
        if not polling_units:
            return LGASummary(
                lga_id=lga_id,
                lga_name=lga.lga_name,
                party_totals=[]
            )
        
        # Get all polling unit IDs
        pu_ids = [str(pu.uniqueid) for pu in polling_units]
        
        # Calculate sum from polling unit results (NOT from announced_lga_results)
        # This sums all party scores from all polling units in this LGA
        party_totals = db.query(
            AnnouncedPUResult.party_abbreviation,
            func.sum(AnnouncedPUResult.party_score).label('total_score')
        ).filter(
            AnnouncedPUResult.polling_unit_uniqueid.in_(pu_ids)
        ).group_by(
            AnnouncedPUResult.party_abbreviation
        ).all()
        
        # Format results
        party_results = [
            PartyResult(
                party_abbreviation=party_abbreviation,
                party_score=int(total_score) if total_score else 0
            )
            for party_abbreviation, total_score in party_totals
        ]
        
        return LGASummary(
            lga_id=lga_id,
            lga_name=lga.lga_name,
            party_totals=party_results
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

