"""
Congress.gov API Integration

Provides access to Congress.gov API for legislative tracking.
https://api.congress.gov/
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog
from pydantic import BaseModel, Field

from core.config import settings

logger = structlog.get_logger()


# =============================================================================
# Response Models
# =============================================================================

class BillSummary(BaseModel):
    """Summary of a bill from Congress.gov."""
    
    congress: int
    bill_type: str
    bill_number: int
    title: str
    origin_chamber: str
    introduced_date: Optional[str] = None
    latest_action_date: Optional[str] = None
    latest_action_text: Optional[str] = None
    policy_area: Optional[str] = None
    update_date: Optional[str] = None
    url: str


class BillDetail(BaseModel):
    """Detailed bill information."""
    
    congress: int
    bill_type: str
    bill_number: int
    title: str
    title_without_office: Optional[str] = None
    introduced_date: Optional[str] = None
    constitutional_authority_statement: Optional[str] = None
    
    # Status
    origin_chamber: str
    origin_chamber_code: Optional[str] = None
    latest_action_date: Optional[str] = None
    latest_action_text: Optional[str] = None
    
    # Classification
    policy_area: Optional[str] = None
    subjects: List[str] = Field(default_factory=list)
    
    # Sponsors
    sponsors: List[Dict[str, Any]] = Field(default_factory=list)
    cosponsors_count: int = 0
    
    # Related
    related_bills: List[Dict[str, Any]] = Field(default_factory=list)
    amendments: List[Dict[str, Any]] = Field(default_factory=list)
    committees: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Full text
    text_versions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    url: str
    update_date: Optional[str] = None


class LegislatorInfo(BaseModel):
    """Information about a legislator."""
    
    bioguide_id: str
    first_name: str
    last_name: str
    party: str
    state: str
    district: Optional[str] = None
    chamber: str  # house or senate
    
    # Contact
    official_url: Optional[str] = None
    
    # Current term
    terms: List[Dict[str, Any]] = Field(default_factory=list)


class CommitteeInfo(BaseModel):
    """Information about a committee."""
    
    system_code: str
    name: str
    chamber: str
    parent_committee: Optional[str] = None
    subcommittees: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Congress.gov API Client
# =============================================================================

class CongressAPIClient:
    """
    Client for the Congress.gov API.
    
    Provides methods for searching bills, tracking legislation,
    and accessing legislator information.
    """
    
    BASE_URL = "https://api.congress.gov/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.congress_api_key
        if not self.api_key:
            logger.warning("Congress.gov API key not configured")
        
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
            headers={"Accept": "application/json"},
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        params = params or {}
        params["api_key"] = self.api_key
        
        try:
            response = await self._client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "Congress API error",
                endpoint=endpoint,
                status=e.response.status_code,
                detail=e.response.text,
            )
            raise
        except Exception as e:
            logger.error("Congress API request failed", error=str(e))
            raise
    
    # =========================================================================
    # Bill Methods
    # =========================================================================
    
    async def search_bills(
        self,
        query: Optional[str] = None,
        congress: Optional[int] = None,
        bill_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[BillSummary]:
        """
        Search for bills.
        
        Args:
            query: Search query (searches title and text)
            congress: Congress number (e.g., 118 for 118th Congress)
            bill_type: Type of bill (hr, s, hjres, sjres, etc.)
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            List of bill summaries
        """
        endpoint = "/bill"
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if congress:
            endpoint = f"/bill/{congress}"
            if bill_type:
                endpoint = f"/bill/{congress}/{bill_type}"
        
        data = await self._request(endpoint, params)
        
        bills = []
        for item in data.get("bills", []):
            try:
                bills.append(BillSummary(
                    congress=item.get("congress"),
                    bill_type=item.get("type", "").lower(),
                    bill_number=item.get("number"),
                    title=item.get("title", ""),
                    origin_chamber=item.get("originChamber", "").lower(),
                    introduced_date=item.get("introducedDate"),
                    latest_action_date=item.get("latestAction", {}).get("actionDate"),
                    latest_action_text=item.get("latestAction", {}).get("text"),
                    policy_area=item.get("policyArea", {}).get("name") if item.get("policyArea") else None,
                    update_date=item.get("updateDate"),
                    url=item.get("url", ""),
                ))
            except Exception as e:
                logger.warning("Failed to parse bill", error=str(e), item=item)
        
        return bills
    
    async def get_bill(
        self,
        congress: int,
        bill_type: str,
        bill_number: int,
    ) -> BillDetail:
        """
        Get detailed information about a specific bill.
        
        Args:
            congress: Congress number
            bill_type: Bill type (hr, s, etc.)
            bill_number: Bill number
        
        Returns:
            Detailed bill information
        """
        endpoint = f"/bill/{congress}/{bill_type.lower()}/{bill_number}"
        data = await self._request(endpoint)
        
        bill = data.get("bill", {})
        
        # Fetch additional details
        sponsors = []
        cosponsors_count = 0
        subjects = []
        committees = []
        
        # Get sponsors
        if "sponsors" in bill:
            sponsors = bill["sponsors"]
        
        # Get cosponsors count
        cosponsors_data = await self._request(f"{endpoint}/cosponsors", {"limit": 1})
        cosponsors_count = cosponsors_data.get("count", 0)
        
        # Get subjects
        subjects_data = await self._request(f"{endpoint}/subjects")
        if "subjects" in subjects_data:
            subjects = [s.get("name") for s in subjects_data.get("subjects", {}).get("legislativeSubjects", [])]
        
        # Get committees
        committees_data = await self._request(f"{endpoint}/committees")
        committees = committees_data.get("committees", [])
        
        return BillDetail(
            congress=bill.get("congress"),
            bill_type=bill.get("type", "").lower(),
            bill_number=bill.get("number"),
            title=bill.get("title", ""),
            title_without_office=bill.get("titleWithoutOffice"),
            introduced_date=bill.get("introducedDate"),
            constitutional_authority_statement=bill.get("constitutionalAuthorityStatementText"),
            origin_chamber=bill.get("originChamber", "").lower(),
            origin_chamber_code=bill.get("originChamberCode"),
            latest_action_date=bill.get("latestAction", {}).get("actionDate"),
            latest_action_text=bill.get("latestAction", {}).get("text"),
            policy_area=bill.get("policyArea", {}).get("name") if bill.get("policyArea") else None,
            subjects=subjects,
            sponsors=sponsors,
            cosponsors_count=cosponsors_count,
            committees=committees,
            url=bill.get("url", ""),
            update_date=bill.get("updateDate"),
        )
    
    async def get_bill_actions(
        self,
        congress: int,
        bill_type: str,
        bill_number: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get actions taken on a bill."""
        endpoint = f"/bill/{congress}/{bill_type.lower()}/{bill_number}/actions"
        data = await self._request(endpoint, {"limit": limit})
        return data.get("actions", [])
    
    async def get_bill_cosponsors(
        self,
        congress: int,
        bill_type: str,
        bill_number: int,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        """Get cosponsors of a bill."""
        endpoint = f"/bill/{congress}/{bill_type.lower()}/{bill_number}/cosponsors"
        data = await self._request(endpoint, {"limit": limit})
        return data.get("cosponsors", [])
    
    async def get_bill_text(
        self,
        congress: int,
        bill_type: str,
        bill_number: int,
    ) -> List[Dict[str, Any]]:
        """Get text versions of a bill."""
        endpoint = f"/bill/{congress}/{bill_type.lower()}/{bill_number}/text"
        data = await self._request(endpoint)
        return data.get("textVersions", [])
    
    async def search_bills_by_keyword(
        self,
        keywords: List[str],
        congress: Optional[int] = None,
        limit: int = 50,
    ) -> List[BillSummary]:
        """
        Search bills containing any of the specified keywords.
        
        This uses the title and summary to find relevant bills.
        """
        # Get recent bills and filter locally
        # Note: Congress.gov API doesn't have a full-text search endpoint
        # In production, you'd want to use a search service
        
        all_bills = await self.search_bills(congress=congress, limit=limit)
        
        keyword_lower = [k.lower() for k in keywords]
        filtered = []
        
        for bill in all_bills:
            title_lower = bill.title.lower()
            if any(kw in title_lower for kw in keyword_lower):
                filtered.append(bill)
        
        return filtered
    
    # =========================================================================
    # Member Methods
    # =========================================================================
    
    async def get_members(
        self,
        congress: Optional[int] = None,
        chamber: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        """
        Get list of Congress members.
        
        Args:
            congress: Congress number
            chamber: 'house' or 'senate'
            limit: Maximum results
        """
        endpoint = "/member"
        params = {"limit": limit}
        
        if congress:
            params["congress"] = congress
        
        if chamber:
            endpoint = f"/member/{chamber}"
        
        data = await self._request(endpoint, params)
        return data.get("members", [])
    
    async def get_member(self, bioguide_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific member."""
        endpoint = f"/member/{bioguide_id}"
        data = await self._request(endpoint)
        return data.get("member", {})
    
    async def get_member_sponsored_legislation(
        self,
        bioguide_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get legislation sponsored by a member."""
        endpoint = f"/member/{bioguide_id}/sponsored-legislation"
        data = await self._request(endpoint, {"limit": limit})
        return data.get("sponsoredLegislation", [])
    
    # =========================================================================
    # Committee Methods
    # =========================================================================
    
    async def get_committees(
        self,
        chamber: Optional[str] = None,
        congress: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of committees."""
        endpoint = "/committee"
        params = {}
        
        if chamber:
            params["chamber"] = chamber
        if congress:
            params["congress"] = congress
        
        data = await self._request(endpoint, params)
        return data.get("committees", [])
    
    async def get_committee(
        self,
        chamber: str,
        committee_code: str,
    ) -> Dict[str, Any]:
        """Get detailed committee information."""
        endpoint = f"/committee/{chamber}/{committee_code}"
        data = await self._request(endpoint)
        return data.get("committee", {})
    
    # =========================================================================
    # Hearing Methods
    # =========================================================================
    
    async def get_hearings(
        self,
        congress: Optional[int] = None,
        chamber: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get upcoming and recent hearings."""
        endpoint = "/hearing"
        params = {"limit": limit}
        
        if congress:
            endpoint = f"/hearing/{congress}"
            if chamber:
                endpoint = f"/hearing/{congress}/{chamber}"
        
        data = await self._request(endpoint, params)
        return data.get("hearings", [])
    
    # =========================================================================
    # Context Managers
    # =========================================================================
    
    async def __aenter__(self) -> "CongressAPIClient":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


# =============================================================================
# Convenience Functions
# =============================================================================

async def search_wireless_power_bills(
    congress: Optional[int] = None,
) -> List[BillSummary]:
    """
    Search for bills related to wireless power/charging.
    
    Default use case for the advocacy system.
    """
    keywords = [
        "wireless power",
        "wireless charging",
        "inductive charging",
        "radio frequency energy",
        "wireless energy",
        "power transmission",
    ]
    
    async with CongressAPIClient() as client:
        return await client.search_bills_by_keyword(keywords, congress=congress)


async def get_current_congress() -> int:
    """Get the current Congress number based on date."""
    # Congress sessions: 1st Congress started 1789
    # New Congress every 2 years starting January
    current_year = datetime.now().year
    return ((current_year - 1789) // 2) + 1
