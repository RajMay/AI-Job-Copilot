"""
Heuristic detection of India-based job locations from scraper text.
Optional filter by Indian state / UT using location string + city inference.
"""

import re
from typing import Any, Dict, List, Optional, Set

# For API docs / UI — same strings should be used in the Streamlit multiselect
INDIAN_STATES_UT: List[str] = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Delhi",
    "Chandigarh",
    "Jammu and Kashmir",
    "Ladakh",
    "Puducherry",
    "Andaman and Nicobar Islands",
]

# lowercase city/area phrase -> state name (must match an entry in INDIAN_STATES_UT or Odisha)
_CITY_TO_STATE: Dict[str, str] = {
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "nagpur": "Maharashtra",
    "thane": "Maharashtra",
    "nashik": "Maharashtra",
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    "mysore": "Karnataka",
    "mysuru": "Karnataka",
    "mangalore": "Karnataka",
    "hubli": "Karnataka",
    "hyderabad": "Telangana",
    "secunderabad": "Telangana",
    "warangal": "Telangana",
    "chennai": "Tamil Nadu",
    "coimbatore": "Tamil Nadu",
    "madurai": "Tamil Nadu",
    "tiruchirappalli": "Tamil Nadu",
    "trichy": "Tamil Nadu",
    "salem": "Tamil Nadu",
    "vellore": "Tamil Nadu",
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "gurgaon": "Haryana",
    "gurugram": "Haryana",
    "faridabad": "Haryana",
    "panipat": "Haryana",
    "noida": "Uttar Pradesh",
    "greater noida": "Uttar Pradesh",
    "ghaziabad": "Uttar Pradesh",
    "lucknow": "Uttar Pradesh",
    "kanpur": "Uttar Pradesh",
    "agra": "Uttar Pradesh",
    "varanasi": "Uttar Pradesh",
    "meerut": "Uttar Pradesh",
    "kolkata": "West Bengal",
    "howrah": "West Bengal",
    "durgapur": "West Bengal",
    "siliguri": "West Bengal",
    "ahmedabad": "Gujarat",
    "surat": "Gujarat",
    "vadodara": "Gujarat",
    "baroda": "Gujarat",
    "rajkot": "Gujarat",
    "jaipur": "Rajasthan",
    "jodhpur": "Rajasthan",
    "udaipur": "Rajasthan",
    "kota": "Rajasthan",
    "indore": "Madhya Pradesh",
    "bhopal": "Madhya Pradesh",
    "gwalior": "Madhya Pradesh",
    "jabalpur": "Madhya Pradesh",
    "kochi": "Kerala",
    "cochin": "Kerala",
    "trivandrum": "Kerala",
    "thiruvananthapuram": "Kerala",
    "kozhikode": "Kerala",
    "calicut": "Kerala",
    "thrissur": "Kerala",
    "visakhapatnam": "Andhra Pradesh",
    "vizag": "Andhra Pradesh",
    "vijayawada": "Andhra Pradesh",
    "guntur": "Andhra Pradesh",
    "tirupati": "Andhra Pradesh",
    "chandigarh": "Chandigarh",
    "ludhiana": "Punjab",
    "amritsar": "Punjab",
    "patiala": "Punjab",
    "patna": "Bihar",
    "gaya": "Bihar",
    "ranchi": "Jharkhand",
    "jamshedpur": "Jharkhand",
    "bhubaneswar": "Odisha",
    "cuttack": "Odisha",
    "rourkela": "Odisha",
    "guwahati": "Assam",
    "dehradun": "Uttarakhand",
    "haridwar": "Uttarakhand",
    "shimla": "Himachal Pradesh",
    "goa": "Goa",
    "panaji": "Goa",
    "srinagar": "Jammu and Kashmir",
    "jammu": "Jammu and Kashmir",
    "leh": "Ladakh",
    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",
    "port blair": "Andaman and Nicobar Islands",
}

# Major Indian cities / regions (lowercase substrings)
_INDIAN_PLACE_TOKENS: tuple = (
    "india",
    "bharat",
    "mumbai",
    "bengaluru",
    "bangalore",
    "hyderabad",
    "pune",
    "chennai",
    "delhi",
    "ncr",
    "gurgaon",
    "gurugram",
    "noida",
    "greater noida",
    "kolkata",
    "calcutta",
    "ahmedabad",
    "jaipur",
    "kochi",
    "coimbatore",
    "indore",
    "bhopal",
    "visakhapatnam",
    "vizag",
    "lucknow",
    "kanpur",
    "nagpur",
    "thane",
    "faridabad",
    "ghaziabad",
    "chandigarh",
    "surat",
    "vadodara",
    "baroda",
    "mysore",
    "mysuru",
    "trivandrum",
    "thiruvananthapuram",
    "kozhikode",
    "calicut",
    "madurai",
    "trichy",
    "tiruchir",
    "vijayawada",
    "nashik",
    "aurangabad",
    "ludhiana",
    "agra",
    "meerut",
    "varanasi",
    "patna",
    "ranchi",
    "guwahati",
    "bhubaneswar",
    "dehradun",
    "mohali",
    "panchkula",
    "karnataka",
    "tamil nadu",
    "telangana",
    "maharashtra",
    "gujarat",
    "west bengal",
    "uttar pradesh",
    "rajasthan",
    "punjab",
    "haryana",
    "kerala",
    "andhra pradesh",
    "madhya pradesh",
    "odisha",
    "orissa",
    "assam",
    "bihar",
    "jharkhand",
    "goa",
)


def is_indian_location(location: str) -> bool:
    """
    True if the location string likely refers to India.
    Remote / worldwide-only strings return False (strict India filter).
    """
    if not location or str(location).strip().upper() == "N/A":
        return False
    s = str(location).lower()
    s = re.sub(r"\s+", " ", s).strip()

    if re.search(r"\bindia\b", s):
        return True

    for token in _INDIAN_PLACE_TOKENS:
        if token == "india":
            continue
        if token in s:
            return True

    return False


def _norm_loc(location: str) -> str:
    return re.sub(r"\s+", " ", (location or "").lower()).strip()


def inferred_india_states_from_location(location: str) -> Set[str]:
    """States/UTs implied by state names or known cities in the location string."""
    loc = _norm_loc(location)
    if not loc:
        return set()
    found: Set[str] = set()
    for state in INDIAN_STATES_UT:
        if state.lower() in loc:
            found.add(state)
    if "orissa" in loc:
        found.add("Odisha")
    for city, state in _CITY_TO_STATE.items():
        if city in loc:
            found.add(state)
    return found


def location_matches_india_states(location: str, selected_states: List[str]) -> bool:
    """True if job location matches at least one selected state/UT (inference)."""
    sel = [s.strip() for s in selected_states if s and str(s).strip()]
    if not sel:
        return True
    inferred = inferred_india_states_from_location(location)
    sel_set = set(sel)
    return bool(inferred & sel_set)


def filter_jobs_by_india_options(
    jobs: List[Dict[str, Any]],
    *,
    india_only: bool = False,
    india_states: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    states = [s.strip() for s in (india_states or []) if s and str(s).strip()]
    out: List[Dict[str, Any]] = []
    for j in jobs:
        loc = j.get("location") or ""
        if india_only and not is_indian_location(loc):
            continue
        if states and not location_matches_india_states(loc, states):
            continue
        out.append(j)
    return out


def filter_jobs_india_only(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Backward-compatible: India-wide only, no state breakdown."""
    return filter_jobs_by_india_options(jobs, india_only=True, india_states=None)
