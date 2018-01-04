from datetime import datetime, timedelta

from .constants import FREE_USER, SUPER_USERS,\
                       MIN_MONTH, MAX_MONTH, FREE_MINUTE

def is_free_user(user_name):
  """ check if user is the free user
  """
  # print(user_name,':',FREE_USER)
  if user_name == FREE_USER:
    return True
  return False

def is_super_user(user_name):
  """ check if user is superuser
  """
  # print(user_name,':',FREE_USER)
  if user_name in SUPER_USERS:
    return True
  return False

def is_normal_user(user_name):
  """ check if user is normal user
  """
  # print(user_name,':',FREE_USER)
  if user_name in SUPER_USERS:
    return False
  return True

def date_is_wrong(date_to_show, date_today):
  """ check plausibility of date
  """
  if ((date_to_show.year != date_today.year) or
      (date_to_show.month < MIN_MONTH) or
      (date_to_show.month > MAX_MONTH)):
    return True
  return False

def get_act_hour():
  """ get begin of current and next hour
  """
  time_now = datetime.now()
  act_hour = time_now - timedelta(minutes=time_now.minute,
                                  seconds=time_now.second,
                                  microseconds=time_now.microsecond)
  next_hour = act_hour + timedelta(hours=1)
  # ab Minute 45 nächste volle Stunde ermitteln
  if time_now.minute >= FREE_MINUTE:
    act_hour += timedelta(hours=1)
  return (act_hour, next_hour)
  