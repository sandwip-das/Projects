import calendar
from datetime import date, timedelta, datetime

def get_years_range(current_year):
    return range(current_year - 50, current_year + 51)

def get_international_roster(year):
    # Reference: Dec 31, 2025 -> Shift B=Morning(1st), C=Evening, D=Night, A=Off.
    # User Requirement:
    # Row 0 of table MUST be: A(M), B(E), C(N), D(O).
    
    # 1. Define the Fixed Backbone of 32 Rows
    # Cycle State 0 for A-Start: A=M1(0), B=E1(2), C=N1(4), D=O1(6).
    initial_offsets = {'A': 0, 'B': 2, 'C': 4, 'D': 6}
    
    rows = []
    for r in range(32):
        row_data = {
            'index': r,
            'M': '', 'E': '', 'N': '', 'O': '',
            'months': {m: None for m in range(1, 13)}, # 1-12
        }
        
        # Populate Shift Columns based on backbone state
        cycle_state = r % 8
        for s_name, start_off in initial_offsets.items():
            # State of shift S at this backbone row
            s_state = (start_off + cycle_state) % 8
            
            if s_state in [0, 1]:
                row_data['M'] = s_name
            elif s_state in [2, 3]:
                row_data['E'] = s_name
            elif s_state in [4, 5]:
                row_data['N'] = s_name
            elif s_state in [6, 7]:
                row_data['O'] = s_name
        rows.append(row_data)

    # 2. Map Dates to Rows
    # Dec 31 2025 Ref (B=M1) corresponds to Backbone State 6.
    # (Because Backbone starts A=M1. A=M1 -> ... -> B=M1 is +6 steps).
    # So Dec 31 2025 is at Row 6 in the modulo-32 cycle.
    
    ref_date = date(2025, 12, 31)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    current = start_date
    while current <= end_date:
        delta = (current - ref_date).days
        
        # Calculate Row Index (0-31)
        # Dec 31 was Row 6.
        # Jan 1 is Row 7.
        row_idx = (6 + delta) % 32
        
        m_idx = current.month
        fmt_date = current.strftime("%d %a-%y")
        
        rows[row_idx]['months'][m_idx] = {
            'text': fmt_date,
            'full_date': current.strftime("%Y-%m-%d"),
            'day': current.day
        }
        
        current += timedelta(days=1)
        
    return rows

def get_domestic_roster(year):
    # Reference: Dec 31 2025
    # Pattern: 6 days.
    # Ref State: A=E(3rd), B=M(3rd).
    # Wait, Jan 1 is start of new block?
    # "Dec 29, 30, 31... morning was B... evening was A"
    # This implies Dec 31 was the 3rd day of that block.
    # So Jan 1 starts a new block 1.
    # Block 1 starts Jan 1.
    # Block 1 logic (Days 0, 1, 2 from Jan 1):
    # Shift A becomes M. Shift B becomes E.
    # Cycle length 6.
    # Offset 0,1,2: A=M, B=E.
    # Offset 3,4,5: A=E, B=M.
    
    data = []
    months = range(1, 13)
    
    # We can just iterate 1 to 31 for rows.
    # But some months don't have 31 days.
    # For a consolidated table, we iterate rows 1..31.
    
    roster_rows = []
    for day_num in range(1, 32):
        row = {'day_num': day_num, 'months': {}}
        for m in months:
            try:
                d = date(year, m, day_num)
                # Calculate shift
                # Delta from Jan 1 of THIS year? 
                # No, delta from known reference Dec 31 2025 to keep sequence valid across years?
                # "it will continue like this no matter what month or year comes next"
                # So we must use the absolute delta from fixed ref (Dec 31 2025).
                
                ref_date = date(2025, 12, 31)
                delta_days = (d - ref_date).days # Jan 1 2026 is delta=1
                
                # Logic:
                # Dec 31 (delta 0) was end of old block.
                # Jan 1 (delta 1) is start of new block.
                # So (delta_days - 1) % 6
                # Index 0,1,2 -> A=M, B=E
                # Index 3,4,5 -> A=E, B=M
                
                cycle_idx = (delta_days - 1) % 6
                
                if 0 <= cycle_idx < 3:
                    m_shift = 'A'
                    e_shift = 'B'
                else:
                    m_shift = 'B'
                    e_shift = 'A'
                    
                row['months'][m] = {
                    'date': d,
                    'day_name': d.strftime("%a"),
                    'M': m_shift,
                    'E': e_shift
                }
            except ValueError:
                # Day doesn't exist (e.g. Feb 30)
                row['months'][m] = None
        roster_rows.append(row)
        
    return roster_rows
