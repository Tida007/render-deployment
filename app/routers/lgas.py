"""Router for LGA endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import logging
from app.database import get_db
from app.models import LGA, PollingUnit, AnnouncedPUResult
from app.schemas import LGASummary, LGAInfo, PartyResult

# Setup logging for production (will appear in Render logs)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/lgas", tags=["lgas"])


@router.get("/", response_model=List[LGAInfo])
def get_all_lgas(db: Session = Depends(get_db)):
    """
    Get list of all LGAs for select box
    
    Used for Feature 2: LGA selection
    """
    try:
        logger.info("Fetching all LGAs")
        lgas = db.query(LGA).order_by(LGA.lga_name).all()
        logger.info(f"Found {len(lgas)} LGAs")
        return [
            LGAInfo(lga_id=lga.lga_id, lga_name=lga.lga_name)
            for lga in lgas
        ]
    except Exception as e:
        logger.error(f"Error fetching LGAs: {str(e)}", exc_info=True)
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
    logger.info(f"get_lga_summary called with lga_id={lga_id}")
    try:
        # Get LGA info
        logger.info(f"Querying LGA with id={lga_id}")
        lga = db.query(LGA).filter(LGA.lga_id == lga_id).first()
        
        if not lga:
            logger.warning(f"LGA not found: {lga_id}")
            raise HTTPException(status_code=404, detail="LGA not found")
        
        logger.info(f"LGA found: {lga.lga_name}")
        
        # Get all polling units in this LGA
        logger.info(f"Querying polling units for LGA {lga_id}")
        polling_units = db.query(PollingUnit).filter(
            PollingUnit.lga_id == lga_id
        ).all()
        
        logger.info(f"Found {len(polling_units)} polling units")
        
        if not polling_units:
            logger.info(f"No polling units found for LGA {lga_id}, returning empty results")
            return LGASummary(
                lga_id=lga_id,
                lga_name=lga.lga_name,
                party_totals=[]
            )
        
        # Get all polling unit IDs
        pu_ids = [str(pu.uniqueid) for pu in polling_units]
        logger.info(f"Polling unit IDs: {len(pu_ids)} units")
        
        # Calculate sum from polling unit results (NOT from announced_lga_results)
        # This sums all party scores from all polling units in this LGA
        logger.info(f"Querying party totals for {len(pu_ids)} polling units")
        party_totals = db.query(
            AnnouncedPUResult.party_abbreviation,
            func.sum(AnnouncedPUResult.party_score).label('total_score')
        ).filter(
            AnnouncedPUResult.polling_unit_uniqueid.in_(pu_ids)
        ).group_by(
            AnnouncedPUResult.party_abbreviation
        ).all()
        
        logger.info(f"Found {len(party_totals)} party results")
        
        # Format results
        party_results = [
            PartyResult(
                party_abbreviation=party_abbreviation,
                party_score=int(total_score) if total_score else 0
            )
            for party_abbreviation, total_score in party_totals
        ]
        
        logger.info(f"Successfully returning summary for LGA {lga_id} with {len(party_results)} parties")
        return LGASummary(
            lga_id=lga_id,
            lga_name=lga.lga_name,
            party_totals=party_results
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        # Log the full error with traceback for production debugging
        logger.error(f"Error in get_lga_summary for lga_id={lga_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

