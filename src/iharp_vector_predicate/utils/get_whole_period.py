import pandas as pd
import calendar


def get_last_date_of_month(dt):
    return calendar.monthrange(dt.year, dt.month)[1]


def get_whole_year_between(start_dt, end_dt):
    assert start_dt.year <= end_dt.year
    start_year = start_dt.year
    end_year = end_dt.year
    first_hour_start_year = pd.Timestamp(f"{start_year}-01-01 00:00:00")
    last_hour_end_year = pd.Timestamp(f"{end_year}-12-31 23:00:00")
    years = list(range(start_year, end_year + 1))
    if start_dt != first_hour_start_year:
        years = years[1:]
    if end_dt != last_hour_end_year:
        years = years[:-1]
    # residual
    residual = []
    last_hour_start_year = pd.Timestamp(f"{start_year}-12-31 23:00:00")
    first_hour_end_year = pd.Timestamp(f"{end_year}-01-01 00:00:00")
    if start_dt != first_hour_start_year and end_dt <= last_hour_start_year:
        residual.append([start_dt, end_dt])
    else:
        if start_dt != first_hour_start_year:
            residual.append([start_dt, last_hour_start_year])
        if end_dt < last_hour_end_year:
            residual.append([first_hour_end_year, end_dt])
    # print("years:", years)
    # print("month residual:", residual)
    return years, residual


def get_whole_month_between(start_dt, end_dt):
    assert start_dt.year == end_dt.year
    year = start_dt.year
    start_month = start_dt.month
    end_month = end_dt.month
    first_hour_start_month = pd.Timestamp(f"{year}-{start_month:02d}-01 00:00:00")
    last_hour_end_month = pd.Timestamp(f"{year}-{end_month:02d}-{get_last_date_of_month(end_dt)} 23:00:00")
    months = [f"{year}-{month:02d}" for month in range(start_month, end_month + 1)]
    if start_dt != first_hour_start_month:
        months = months[1:]
    if end_dt != last_hour_end_month:
        months = months[:-1]
    # residual
    residual = []
    last_hour_start_month = pd.Timestamp(f"{year}-{start_month:02d}-{get_last_date_of_month(start_dt)} 23:00:00")
    first_hour_end_month = pd.Timestamp(f"{year}-{end_month:02d}-01 00:00:00")
    if start_dt != first_hour_start_month and end_dt <= last_hour_start_month:
        residual.append([start_dt, end_dt])
    else:
        if start_dt != first_hour_start_month:
            residual.append([start_dt, last_hour_start_month])
        if end_dt < last_hour_end_month:
            residual.append([first_hour_end_month, end_dt])
    # print("months:", months)
    # print("day residual:", residual)
    return months, residual


def get_whole_day_between(start_dt, end_dt):
    assert start_dt.year == end_dt.year
    assert start_dt.month == end_dt.month
    year = start_dt.year
    month = start_dt.month
    start_day = start_dt.day
    end_day = end_dt.day
    first_hour_start_day = pd.Timestamp(f"{year}-{month:02d}-{start_day:02d} 00:00:00")
    last_hour_end_day = pd.Timestamp(f"{year}-{month:02d}-{end_day:02d} 23:00:00")
    days = [f"{year}-{month:02d}-{day:02d}" for day in range(start_day, end_day + 1)]
    if start_dt != first_hour_start_day:
        days = days[1:]
    if end_dt != last_hour_end_day:
        days = days[:-1]
    # residual
    residual = []
    last_hour_start_day = pd.Timestamp(f"{year}-{month:02d}-{start_day:02d} 23:00:00")
    first_hour_end_day = pd.Timestamp(f"{year}-{month:02d}-{end_day:02d} 00:00:00")
    if start_dt != first_hour_start_day and end_dt <= last_hour_start_day:
        residual.append([start_dt, end_dt])
    else:
        if start_dt != first_hour_start_day:
            residual.append([start_dt, last_hour_start_day])
        if end_dt < last_hour_end_day:
            residual.append([first_hour_end_day, end_dt])
    # print("days:", days)
    # print("hour residual:", residual)
    return days, residual


def get_whole_hour_between(start_dt, end_dt):
    assert start_dt.year == end_dt.year
    assert start_dt.month == end_dt.month
    assert start_dt.day == end_dt.day
    year = start_dt.year
    month = start_dt.month
    day = start_dt.day
    start_hour = start_dt.hour
    end_hour = end_dt.hour
    hours = [f"{year}-{month:02d}-{day:02d} {hour:02d}:00:00" for hour in range(start_hour, end_hour + 1)]
    # print("hours:", hours)
    return hours


def get_whole_period_between(start, end):
    start_dt = pd.Timestamp(start)
    end_dt = pd.Timestamp(end)
    whole_months = []
    whole_days = []
    whole_hours = []
    whole_years, residual = get_whole_year_between(start_dt, end_dt)
    for res in residual:
        months, residual = get_whole_month_between(pd.Timestamp(res[0]), pd.Timestamp(res[1]))
        whole_months.extend(months)
        for res in residual:
            days, residual = get_whole_day_between(pd.Timestamp(res[0]), pd.Timestamp(res[1]))
            whole_days.extend(days)
            for res in residual:
                hours = get_whole_hour_between(pd.Timestamp(res[0]), pd.Timestamp(res[1]))
                whole_hours.extend(hours)
    print("******************")
    print("whole year")
    for y in whole_years:
        print(y)
    print("whole month")
    for m in whole_months:
        print(m)
    print("whole day")
    for d in whole_days:
        print(d)
    print("whole hour")
    for h in whole_hours:
        print(h)
    return whole_years, whole_months, whole_days, whole_hours


def get_whole_ranges_between(start, end):
    year_range = []
    month_range = []
    day_range = []
    hour_range = []
    start_dt = pd.Timestamp(start)
    end_dt = pd.Timestamp(end)
    whole_years, residual = get_whole_year_between(start_dt, end_dt)
    if whole_years:
        year_start = pd.Timestamp(f"{whole_years[0]}-01-01 00:00:00")
        year_end = pd.Timestamp(f"{whole_years[-1]}-12-31 23:00:00")
        year_range.append([year_start, year_end])
    for res in residual:
        months, residual = get_whole_month_between(pd.Timestamp(res[0]), pd.Timestamp(res[1]))
        if months:
            month_start = pd.Timestamp(f"{months[0]}-01 00:00:00")
            month_end = pd.Timestamp(f"{months[-1]}-{get_last_date_of_month(pd.Timestamp(months[-1]))} 23:00:00")
            month_range.append([month_start, month_end])
        for res in residual:
            days, residual = get_whole_day_between(pd.Timestamp(res[0]), pd.Timestamp(res[1]))
            if days:
                day_start = pd.Timestamp(f"{days[0]} 00:00:00")
                day_end = pd.Timestamp(f"{days[-1]} 23:00:00")
                day_range.append([day_start, day_end])
            for res in residual:
                hour_start = pd.Timestamp(f"{res[0]}")
                hour_end = pd.Timestamp(f"{res[1]}")
                hour_range.append([hour_start, hour_end])
    print("******************")
    print("year range")
    for y in year_range:
        print(y)
    print("month range")
    for m in month_range:
        print(m)
    print("day range")
    for d in day_range:
        print(d)
    print("hour range")
    for h in hour_range:
        print(h)
    return year_range, month_range, day_range, hour_range


def get_total_hours_in_year(year):
    return 24 * 366 if calendar.isleap(year) else 24 * 365


def get_total_hours_in_month(month):
    return 24 * get_last_date_of_month(pd.Timestamp(month))


def get_total_hours_between(start, end):
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    return int((end_dt - start_dt) / pd.Timedelta("1 hour")) + 1


def iterate_months(start_month, end_month):
    start_month = pd.to_datetime(start_month)
    end_month = pd.to_datetime(end_month)
    for n in range((end_month.year - start_month.year) * 12 + end_month.month - start_month.month + 1):
        yield start_month + pd.DateOffset(months=n)


def number_of_days_inclusive(start_day, end_day):
    start_day = pd.to_datetime(start_day)
    end_day = pd.to_datetime(end_day)
    return (end_day - start_day).days + 1


def number_of_hours_inclusive(start_hour, end_hour):
    start_hour = pd.to_datetime(start_hour)
    end_hour = pd.to_datetime(end_hour)
    return int((end_hour - start_hour) / pd.Timedelta(hours=1)) + 1


def time_array_to_range(time_array, resolution):
    """
    Range: [[pd.Timestamp(start), pd.Timestamp(end)], ...]
    """
    # quick fix for single year
    if resolution == "year" and len(time_array) == 1:
        single_year = time_array[0]
        return [[pd.Timestamp(f"{single_year}-01-01 00:00:00"), pd.Timestamp(f"{single_year}-12-31 23:00:00")]]

    if len(time_array) == 0:
        return []

    if resolution == "year":
        pd_delta = pd.Timedelta(days=366)
        time_array = [f"{year}-01-01" for year in time_array]
    elif resolution == "month":
        pd_delta = pd.Timedelta(days=31)
    elif resolution == "day":
        pd_delta = pd.Timedelta(days=1)
    elif resolution == "hour":
        pd_delta = pd.Timedelta(hours=1)

    sorted_array = sorted(time_array)
    time_range = []
    start = sorted_array[0]
    start_dt = pd.Timestamp(start)
    end_dt = start_dt
    for time in sorted_array[1:]:
        if pd.Timestamp(time) - end_dt > pd_delta:
            time_range.append([start_dt, end_dt])
            start_dt = pd.Timestamp(time)
        end_dt = pd.Timestamp(time)
    if start_dt != end_dt:
        time_range.append([start_dt, end_dt])

    # post processing
    if resolution == "year":
        for r in time_range:
            r[1] = pd.Timestamp(f"{r[1].year}-12-31 23:00:00")
    elif resolution == "month":
        for r in time_range:
            r[1] = pd.Timestamp(f"{r[1].year}-{r[1].month}-{get_last_date_of_month(r[1])} 23:00:00")
    elif resolution == "day":
        for r in time_range:
            r[1] = pd.Timestamp(f"{r[1].year}-{r[1].month}-{r[1].day} 23:00:00")

    return time_range
