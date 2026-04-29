from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AttendanceRow:
    date: str
    day_of_week: str
    start: str
    end: str
    break_minutes: Optional[int] = None      # רק Type A
    total_hours: Optional[float] = None
    hours_100: Optional[float] = None
    hours_125: Optional[float] = None
    hours_150: Optional[float] = None
    hours_shabbat: Optional[float] = None
    location: Optional[str] = None           # רק Type A (גליליון וכו')
    notes: Optional[str] = None              # רק Type B (הערות כמו "ראש השנה")
    is_shabbat: bool = False
    is_holiday: bool = False

@dataclass
class AttendanceReport:
    employee_name: str
    month: str
    year: str
    report_type: str                         # "A" או "N"
    rows: tuple = field(default_factory=tuple)
    
    # סיכומים
    total_days: Optional[int] = None
    total_hours_100: Optional[float] = None
    total_hours_125: Optional[float] = None
    total_hours_150: Optional[float] = None
    total_hours_shabbat: Optional[float] = None
    hourly_rate: Optional[float] = None      # רק Type B (מחיר לשעה)
    total_payment: Optional[float] = None    # רק Type B (סה"כ לתשלום)