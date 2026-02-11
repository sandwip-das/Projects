from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .utils import get_international_roster, get_domestic_roster, get_years_range

def index(request):
    current_year = datetime.now().year
    return redirect('international_roster', year=current_year)

def international_roster(request, year):
    rows = get_international_roster(year)
    years = get_years_range(datetime.now().year)
    today_date = datetime.now()
    today_str = today_date.strftime("%Y-%m-%d")
    
    # Logic: Night shift (22:00 - 06:00) belongs to the date the shift STARTED.
    # If time is 00:00 - 06:00, the effective duty date is Yesterday.
    if today_date.hour < 6:
        active_duty_date = today_date - timedelta(days=1)
    else:
        active_duty_date = today_date
        
    active_duty_str = active_duty_date.strftime("%Y-%m-%d")
    
    # Mark rows
    for row in rows:
        row['is_active_duty'] = False
        # Check if this row represents the active duty date
        # The row contains dates for different months. We need to find if THIS row contains the active_duty_date.
        # Since the structure is: Row X is active_duty_date if (active_duty_date) lands on that row.
        # We can check values.
        for m_data in row['months'].values():
            if m_data and m_data['full_date'] == active_duty_str:
                row['is_active_duty'] = True
                break
                
    context = {
        'rows': rows,
        'year': year,
        'years': years,
        'roster_type': 'international',
        'prev_year': year - 1,
        'next_year': year + 1,
        'today': today_str,
        'current_hour': datetime.now().hour
    }
    return render(request, 'rosterApp/international.html', context)

def domestic_roster(request, year):
    rows = get_domestic_roster(year)
    years = get_years_range(datetime.now().year)
    context = {
        'rows': rows,
        'year': year,
        'years': years,
        'roster_type': 'domestic',
        'prev_year': year - 1,
        'next_year': year + 1,
         'today': datetime.now().strftime("%Y-%m-%d"),
    }
    return render(request, 'rosterApp/domestic.html', context)
