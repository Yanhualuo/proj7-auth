"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#

max_speed = {200: 34, 400: 32, 600:30, 1000: 28, 1300: 26}
min_speed = {200: 15, 400: 15, 600:15, 1000: 11.428, 1300:13.333}

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    if control_dist_km == 0:
        return brevet_start_time.isoformat()
    elif control_dist_km < 0:
        return "Invalid date"

    time = 0.0
    distance = 0
    
    for bre in max_speed:
       spd = max_speed.get(bre)
       if (int(control_dist_km) >= bre):
           time += 200/spd
           distance = bre       
       else:
           lo = control_dist_km - distance
           time += (lo/spd)
           break
    time = round(time * 60) #convert into minutes
    arw = arrow.get(brevet_start_time)
    arw = arw.shift(minutes=+time)
    
    
    return arw.isoformat()

def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    if control_dist_km == 0:
        return brevet_start_time.isoformat()
    elif control_dist_km < 0:
        return "Invalid date"
    
    time = 0.0
    distance = 0
    
    for bre in min_speed:
       spd = min_speed.get(bre)
       if (int(control_dist_km) >= bre):
           time += 200/spd
           distance = bre       
       else:
           lo = control_dist_km - distance
           time += (lo/spd)
           break
    print("hour is ", time)
    time = round(time * 60) #convert into minutes
    arw = arrow.get(brevet_start_time)
    arw = arw.shift(minutes=+time)
    
    
    return arw.isoformat()
