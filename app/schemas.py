"""Pydantic schemas for API request/response validation"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PartyResult(BaseModel):
    """Individual party result"""
    party_abbreviation: str
    party_score: int

    class Config:
        from_attributes = True


class PollingUnitResult(BaseModel):
    """Polling unit with its results"""
    polling_unit_id: int
    polling_unit_name: Optional[str]
    polling_unit_number: Optional[str]
    lga_id: int
    results: List[PartyResult]

    class Config:
        from_attributes = True


class LGASummary(BaseModel):
    """LGA summary with total votes per party"""
    lga_id: int
    lga_name: str
    party_totals: List[PartyResult]

    class Config:
        from_attributes = True


class LGAInfo(BaseModel):
    """Basic LGA information"""
    lga_id: int
    lga_name: str

    class Config:
        from_attributes = True


class StoreResultRequest(BaseModel):
    """Request schema for storing polling unit results"""
    party_results: List[PartyResult]
    entered_by_user: str = "system"
    user_ip_address: Optional[str] = None


class StoreResultResponse(BaseModel):
    """Response schema for storing results"""
    success: bool
    message: str
    polling_unit_uniqueid: str

