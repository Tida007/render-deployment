"""Router for polling unit endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import PollingUnit, AnnouncedPUResult, Party
from app.schemas import PollingUnitResult, PartyResult, StoreResultRequest, StoreResultResponse
from datetime import datetime

router = APIRouter(prefix="/polling-units", tags=["polling-units"])


@router.get("/{polling_unit_id}", response_model=PollingUnitResult)
def get_polling_unit_results(
    polling_unit_id: int,
    db: Session = Depends(get_db)
):
    """
    Get results for a specific polling unit
    
    Feature 1: Display individual polling unit results
    """
    # Get polling unit
    polling_unit = db.query(PollingUnit).filter(
        PollingUnit.uniqueid == polling_unit_id
    ).first()
    
    if not polling_unit:
        raise HTTPException(status_code=404, detail="Polling unit not found")
    
    # Get results for this polling unit
    results = db.query(AnnouncedPUResult).filter(
        AnnouncedPUResult.polling_unit_uniqueid == str(polling_unit_id)
    ).all()
    
    # Format results
    party_results = [
        PartyResult(
            party_abbreviation=result.party_abbreviation,
            party_score=result.party_score
        )
        for result in results
    ]
    
    return PollingUnitResult(
        polling_unit_id=polling_unit.uniqueid,
        polling_unit_name=polling_unit.polling_unit_name,
        polling_unit_number=polling_unit.polling_unit_number,
        lga_id=polling_unit.lga_id,
        results=party_results
    )


@router.post("/{polling_unit_id}/results", response_model=StoreResultResponse)
def store_polling_unit_results(
    polling_unit_id: int,
    request: StoreResultRequest,
    db: Session = Depends(get_db)
):
    """
    Store results for all parties in a polling unit
    
    Feature 3: Store result for all parties polling for a polling unit
    """
    # Verify polling unit exists
    polling_unit = db.query(PollingUnit).filter(
        PollingUnit.uniqueid == polling_unit_id
    ).first()
    
    if not polling_unit:
        raise HTTPException(status_code=404, detail="Polling unit not found")
    
    # Use polling_unit_id from path, ignore it from request body if present
    pu_uniqueid = str(polling_unit_id)
    
    # Store each party result
    stored_count = 0
    for party_result in request.party_results:
        # Check if result already exists
        existing = db.query(AnnouncedPUResult).filter(
            AnnouncedPUResult.polling_unit_uniqueid == pu_uniqueid,
            AnnouncedPUResult.party_abbreviation == party_result.party_abbreviation
        ).first()
        
        if existing:
            # Update existing result
            existing.party_score = party_result.party_score
            existing.entered_by_user = request.entered_by_user
            existing.date_entered = datetime.now()
            existing.user_ip_address = request.user_ip_address or None
        else:
            # Create new result
            new_result = AnnouncedPUResult(
                polling_unit_uniqueid=pu_uniqueid,
                party_abbreviation=party_result.party_abbreviation,
                party_score=party_result.party_score,
                entered_by_user=request.entered_by_user,
                date_entered=datetime.now(),
                user_ip_address=request.user_ip_address or None
            )
            db.add(new_result)
        stored_count += 1
    
    try:
        db.commit()
        return StoreResultResponse(
            success=True,
            message=f"Successfully stored {stored_count} party results",
            polling_unit_uniqueid=pu_uniqueid
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error storing results: {str(e)}")

