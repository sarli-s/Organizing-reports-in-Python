import re
from abc import ABC, abstractmethod
from datetime import datetime

class BaseParser(ABC):
    def __init__(self):
        self.date_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4})'
        self.time_pattern = r'(\d{1,2}:\d{2})'

    @abstractmethod
    def parse_line(self, line):
        pass

class ParserA(BaseParser):
    def parse_line(self, line):
        clean_line = line.replace('"', '').replace("'", "").replace('\\n', ' ')
        
        # מחלצים את כל התאריכים בשורה
        found_dates = re.findall(self.date_pattern, clean_line)
        # מחלצים את כל השעות בשורה (שאינן 00:30)
        all_times = re.findall(self.time_pattern, clean_line)
        work_times = [t for t in all_times if t != "00:30"]

        results = []
        # רצים על התאריכים שמצאנו ומצמידים להם שעות לפי הסדר
        for i in range(len(found_dates)):
            time_idx = i * 2
            if time_idx + 1 < len(work_times):
                results.append({
                    "date": found_dates[i],
                    "start": work_times[time_idx],
                    "end": work_times[time_idx + 1],
                    "break": "00:30"
                })
        return results # מחזיר רשימה!

class ParserN(BaseParser):
    def parse_line(self, line):
        # סוג N בד"כ ישר יותר, אבל נחזיר רשימה למען האחידות
        date_match = re.search(self.date_pattern, line)
        times = re.findall(self.time_pattern, line)
        
        if date_match and len(times) >= 2:
            return [{
                "date": date_match.group(1),
                "start": times[0],
                "end": times[1],
                "break": "00:00"
            }]
        return []