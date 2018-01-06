#!/home/tcz/django/venv/bin/python

from datetime import date, timedelta, datetime
from tkinter import ttk
import tkinter
import tkinter.messagebox
import math
import locale
import os
import sys
from threading import Timer
import urllib.request
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
import json
import django
from courts.constants import BG_FREE,\
                             BG_OTHER,\
                             BG_FREEHOUR,\
                             NUM_COURTS,\
                             HOURS_PER_DAY,\
                             MAX_FUTURE_DAYS,\
                             HOUR_START,\
                             FREE_USER,\
                             ERR_OTHER_USER,\
                             ERR_DATE_INVALID,\
                             ERR_NO_RESERVATION,\
                             ERR_HISTORY_CHANGE
from courts.common import is_normal_user,\
                          get_act_hour

# to allow access to the courts imports and DJANGO environment for database
# sys.path.append('./')

# imports for working in Django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'tcz.settings'
django.setup()
from django.contrib.auth.models import User

# imports to use Django REST framework
URL_GETUSERS = 'http://127.0.0.1:8000/tczusers.json/'
URL_GETHOURS = 'http://127.0.0.1:8000/tczhours.json/'
URL_GETHOURS_DATE = 'http://127.0.0.1:8000/tczhours/atdate.json/?year=%d&month=%d&day=%d'
URL_GETHOURS_FROMNOW = 'http://127.0.0.1:8000/tczhours/fromnow.json/'
URL_POSTHOUR = 'http://127.0.0.1:8000/tczhours/%s/'

URL_GETUSERS = 'http://tczellerndorf.pythonanywhere.com/tczusers.json/'
URL_GETHOURS = 'http://tczellerndorf.pythonanywhere.com/tczhours.json/'
URL_GETHOURS_DATE = 'http://tczellerndorf.pythonanywhere.com/tczhours/atdate.json/?year=%d&month=%d&day=%d'
URL_GETHOURS_FROMNOW = 'http://tczellerndorf.pythonanywhere.com/tczhours/fromnow.json/'
URL_POSTHOUR = 'http://tczellerndorf.pythonanywhere.com/tczhours/%s/'

# token for Raspi
HTTP_HEADER = {
    'Authorization' : 'Token 4069b72a06b076a32df8a6088a662a2e8536e4c8',
    'Accept': '*/*',
}
# token for PC
HTTP_HEADER = {
    'Authorization' : 'Token e1e1a4e114cbbbcf9451f96a4042f5c9b06e841c',
    'Accept': '*/*',
}
FONT14BOLD = ('Verdana', 14, 'bold')
FONT14NORMAL = ('Verdana', 14)
FONT12BOLD = ('Verdana', 12, 'bold')
FONT10BOLD = ('Verdana', 10, 'bold')
FONT18BOLD = ('Verdana', 18, 'bold')
FONT18NORMAL = ('Verdana', 18)
LAB_BACKGROUND = '#7F7F7F'
INITIAL_USER = 'Bitte auswählen'

def get_date_text(i_date):
  """ set locale for Date format - windows is different
  """
  if os.name == 'nt':
    locale.setlocale(locale.LC_TIME, "deu_deu")
  else:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
  return i_date.strftime('%A, %d %B %Y')

def get_date_name(i_date):
  """ set locale for Date format
  """
  if os.name == 'nt':
    locale.setlocale(locale.LC_TIME, "deu_deu")
  else:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
  return i_date.strftime('%Y-%m-%d')

def name_to_text(i_name):
  """ return text
  """
  return i_name

def user_has_reservation(i_user):
  """ for a normal user only 2 hours in the future are allowed
  """
  try:
    #datenow = date.today()
    #lHourCount = 0
    #for l_tczhour in TczHour.objects.filter(tcz_user=i_user)
    #                              .filter(tcz_date__gte=datenow)
    #                              .order_by('tcz_date','tcz_hour'):
    #  if (not l_tczhour.tcz_free) :
    # found an already reserved hour for this week
    #    lHourCount += 1
    #    if (lHourCount == MAX_RESERVATION_DAYS):
    #      return(lHourCount)
    return None
  except:
    return None

def now_string():
  """ returns current date as string
  """
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class ReservationButton():
  """ Button used for the reservation display
  """
  def __init__(self, app, court, hour):
    self.app = app
    self.frame = app.frame2
    self.court = court
    self.hour = hour
    self.but = ttk.Label(self.frame, width=20, text='',
                         font=FONT14BOLD, background=BG_FREE, anchor=tkinter.CENTER)
    self.but.bind("<Button-1>", self.but_pressed)
    self.but.grid(row=self.hour+2-HOUR_START, column=self.court+1,
                  padx=1, pady=1, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

  def but_pressed(self, event):
    """ event when button is pressed
    """
    # print('pressed court=%d, hour=%d' % (self.court,self.hour))
    if self.app.user_name == INITIAL_USER:
      tkinter.messagebox.showerror('Fehler', 'Bitte zuerst Mitglied auswählen')
    else:
      if self.but['text'] == FREE_USER:
        self.app.insert_tcz_hour(self.court, self.hour)
      else:
        # self.text = FREE_USER
        if self.app.user_name == self.but['text']:
          self.app.delete_tcz_hour(self.court, self.hour)
        else:
          tkinter.messagebox.showerror('Fehler', ERR_OTHER_USER % self.but['text'])

class ReservationApp(tkinter.Frame):
  """ the app
  """
  def __init__(self, *args, **kwargs):
    tkinter.Frame.__init__(self, *args, **kwargs)

    self.error_http = False
    self.error_url = False
    self.tk_datename = tkinter.StringVar()
    self.user_name = INITIAL_USER
    self.tk_message = tkinter.StringVar()

    self.frame1 = ttk.Frame(self)
    self.frame2 = ttk.Frame(self)
    self.frame3 = ttk.Frame(self)
    self.frame1.pack(fill=tkinter.X)
    self.frame2.pack(expand=1, fill=tkinter.BOTH)
    self.frame3.pack(fill=tkinter.X)

    self.reserved_hours = {}
    self.ui_make_header()
    self.ui_make_main()
    self.ui_make_footer()
    self.get_all_users()
    self.do_date_today(update=False)

    self.get_all_hours()
    # start update timer_all
    self.timer = Timer(30.0, self.update_fromnow_hours)
    self.timer.start()

  def request_from_server(self, request, errortext):
    """ request data from server
    """
    self.error_http = False
    self.error_url = False
    try:
      self.response = urllib.request.urlopen(request)
    except HTTPError as e_exc:
      print("server couldn't fulfill the request, Error code: ", e_exc.code, e_exc.reason)
      self.error_http = True
      self.response = None
    except URLError as e_exc:
      print('Failed to reach a server, Reason: ', e_exc.reason)
      self.error_url = True
      self.response = None

    if self.error_url:
      # the server cannot be reached
      self.tk_message.set('%s: Serverproblem %s' % (now_string(), errortext))
      self.lab_message.configure(background='red')
      return False
    if self.error_http:
      # server check of request was not successful
      self.tk_message.set('%s: Serverproblem %s' % (now_string(), errortext))
      self.lab_message.configure(background='orange')
      return False
    # no problems
    self.lab_message.configure(background='green')
    return True

  def get_all_users(self):
    """ get the users from the server database
    """
    # self.allUsers = []
    self.user_names_norm = []
    self.user_names_super = []
    self.user_name_to_id = {}
    self.user_id_to_name = {}

    req = urllib.request.Request(URL_GETUSERS, data=None, headers=HTTP_HEADER)
    if self.request_from_server(req, 'Mitgliederliste wird lokal gelesen'):
      # everything is fine
      result = json.loads(self.response.read())
      # print(result)
      # result = User.objects.all().order_by('username')
      # result contains all users sorted by user_names_norm
      # fields = ('id', 'username', 'is_staff', 'first_name', 'last_name')
      for item in result:
        # print(item['username'])
        # self.allUsers.append(item)
        self.user_name_to_id[item['username']] = item['id']
        self.user_id_to_name[item['id']] = item['username']
        if is_normal_user(item['username']):
          self.user_names_norm.append(item['username'])
        else:
          self.user_names_super.append(item['username'])
    else:
      # read Mitglieder from local database
      result = User.objects.all().order_by('username')
      for item in result:
        self.user_name_to_id[item.username] = item.id
        self.user_id_to_name[item.id] = item.username
        if is_normal_user(item.username):
          self.user_names_norm.append(item.username)
        else:
          self.user_names_super.append(item.username)

  def get_tcz_hours(self, url):
    """ get the reserved hours from the server database
    """
    # self.reserved_hours.clear()
    req = urllib.request.Request(url, data=None, headers=HTTP_HEADER, method='GET')
    if self.request_from_server(req, 'Aktualisierung nicht möglich'):
      # everything is fine
      result = json.loads(self.response.read())
      # result contains all reserved hours
      # fields = ('id','tcz_date','tcz_user','tcz_user_change','tcz_court','tcz_hour','tcz_free')
      # append the received items to the reservedhours
      for item in result:
        l_itemdate = datetime.strptime(item['tcz_date'], "%Y-%m-%d").date()
        if l_itemdate in self.reserved_hours:
          self.reserved_hours[l_itemdate].append(item)
        else:
          self.reserved_hours[l_itemdate] = [item]
      return True
    # server problem
    return False

  def get_all_hours(self):
    """ get all hours
    """
    for l_date in self.reserved_hours:
      self.reserved_hours[l_date].clear()
    if self.get_tcz_hours(URL_GETHOURS):
      self.do_update_mainframe()

  def get_fromnow_hours(self):
    """ get all hours
    """
    for l_date in self.reserved_hours:
      if l_date > date.today():
        self.reserved_hours[l_date].clear()
    if self.get_tcz_hours(URL_GETHOURS_FROMNOW):
      self.do_update_mainframe()

  def get_date_hours(self, i_date):
    """ update the hours for the date
    """
    if i_date in self.reserved_hours:
      self.reserved_hours[i_date].clear()
    if self.get_tcz_hours(URL_GETHOURS_DATE % (i_date.year, i_date.month, i_date.day)):
      self.do_update_mainframe()

  def update_curr_hours(self):
    """ update current date
    """
    self.get_date_hours(self.current_date)

  def update_fromnow_hours(self):
    """ update all relevant reserved hours
    """
    # destroy all data which will be requested
    self.get_fromnow_hours()
    print('restart timer: '+ str(datetime.now()))
    self.timer.cancel()
    self.timer = Timer(3600.0, self.update_fromnow_hours)
    self.timer.start()

  def delete_tcz_hour(self, court, hour):
    """ delete the hour
    """
    l_errormessage = ''
    # normal users are not allowed to change the past
    if is_normal_user(self.user_name):
      l_tcztime = datetime(year=self.current_date.year,
                           month=self.current_date.month,
                           day=self.current_date.day,
                           hour=hour)
      l_acthour, l_nexthour = get_act_hour()
      # dont allow modifications of the past
      if l_tcztime < l_acthour:
        l_errormessage = ERR_HISTORY_CHANGE
        tkinter.messagebox.showerror('Fehler', l_errormessage)

    if l_errormessage == '':
      l_hourid = -1
      # search for the specified hour
      for l_tczhour in self.reserved_hours[self.current_date]:
        if ((l_tczhour['tcz_date'] == self.curr_date_name) and
            (l_tczhour['tcz_court'] == court) and
            (l_tczhour['tcz_hour'] == hour)):
          print('Delete Datum=%s Stunde=%s court=%s user=%s' % \
                (self.curr_date_name, hour, court, self.user_name))
          l_hourid = l_tczhour['id']
          break
      if l_hourid != -1:
        req = urllib.request.Request(URL_POSTHOUR % l_hourid,
                                     data=None,
                                     headers=HTTP_HEADER,
                                     method='DELETE')
        if self.request_from_server(req, 'Stunde kann nicht storniert werden'):
          # everything is fine - refresh from the database
          self.tk_message.set('%s: Stornierung für %s durchgeführt' % (now_string(), self.user_name))
          self.get_date_hours(self.current_date)

  def insert_tcz_hour(self, court, hour):
    """ reserve one hour
    """
    # freehours are not counted to the hour budget
    l_freehour = False
    # create time object for reservation time
    l_tcztime = datetime(year=self.current_date.year,
                         month=self.current_date.month,
                         day=self.current_date.day,
                         hour=hour)
    l_normaluser = is_normal_user(self.user_name)
    l_today = date.today()
    l_errormessage = ''
    if l_normaluser:
      l_acthour, l_nexthour = get_act_hour()
      if self.current_date > l_today + timedelta(days=MAX_FUTURE_DAYS):
        l_errormessage = ERR_DATE_INVALID % (self.current_date.day, self.current_date.month, self.current_date.year)
        tkinter.messagebox.showerror('Fehler', l_errormessage)
      # dont allow modifications of the past
      elif l_tcztime < l_acthour:
        l_errormessage = ERR_HISTORY_CHANGE
        tkinter.messagebox.showerror('Fehler', l_errormessage)
      # check if this is a free hour
      elif l_tcztime == l_acthour:
        # mark spezial reservations for current hour and next hour after minute 45
        # there is no limit for free hours
        l_freehour = True
      elif False:
        # check for the maximum of reserved hours
        pass

    if l_errormessage == '':
      print('Insert Datum=%s Stunde=%s court=%s user=%s' % (self.curr_date_name, hour, court, self.user_name))
      l_post = {'tcz_date': self.curr_date_name,
                'tcz_user': int(self.user_name_to_id[self.user_name]),
                'tcz_user_change': 'TCZ',
                'tcz_court': court,
                'tcz_hour': hour,
                'tcz_free': l_freehour,
               }
      # encode data to a byte stream
      params = urlencode(l_post).encode('utf-8')

      req = urllib.request.Request(URL_GETHOURS, data=params, headers=HTTP_HEADER, method='POST')
      if self.request_from_server(req, ERR_NO_RESERVATION % self.user_name):
        # refresh from the database
        self.tk_message.set('%s: Reservierung für %s durchgeführt' % (now_string(), self.user_name))
        self.get_date_hours(self.current_date)

  def ui_make_header(self):
    """ make the header of the app
    """
    style = ttk.Style()
    style.configure('Date.TButton', font=FONT18BOLD)
    self.but_prev = ttk.Button(self.frame1, text='<', command=self.do_date_prev, style='Date.TButton')
    self.but_next = ttk.Button(self.frame1, text='>', command=self.do_date_next, style='Date.TButton')
    self.but_today = ttk.Button(self.frame1, text='Heute', command=self.do_date_today, style='Date.TButton')
    self.lab_date = ttk.Label(self.frame1, textvariable=self.tk_datename,
                              font=FONT18BOLD,
                              width=25)
    self.lab_hint = ttk.Label(self.frame1, text='Reservieren/Freigeben für:',
                              font=FONT14NORMAL)
    self.lab_hint.bind("<Double-1>", self.ui_make_user_super)
    self.but_user = ttk.Button(self.frame1, text=self.user_name, style='Date.TButton', width=25)
    self.but_user.bind("<Button-1>", self.ui_make_user_normal)
    self.but_today.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.but_prev.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.lab_date.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.but_next.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.lab_hint.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5, anchor='w')
    self.but_user.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5, expand=1, fill=tkinter.X)

  def ui_make_main(self):
    """ make the main window
    """
    # let the row grow (weight=1)
    tkinter.Grid.rowconfigure(self.frame2, 1, weight=1)
    # tkinter.Grid.columnconfigure(self.frame2, 1, weight=1)
    self.all_buttons = []

    l_lab = ttk.Label(self.frame2, text='Stunde', width=10,
                      font=FONT14BOLD, background=LAB_BACKGROUND, anchor=tkinter.CENTER)
    l_lab.grid(row=1, column=1, padx=3, pady=3, sticky=tkinter.N+tkinter.S)
    for i in range(NUM_COURTS):
      tkinter.Grid.columnconfigure(self.frame2, i+2, weight=1)
      l_lab = ttk.Label(self.frame2, text='Platz %d' % (i+1),
                        font=FONT14BOLD, background=LAB_BACKGROUND, anchor=tkinter.CENTER)
      l_lab.grid(row=1, column=i+2, padx=3, pady=3, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

    l_row = 1
    for hour in range(HOUR_START, HOUR_START+HOURS_PER_DAY):
      l_row += 1
      tkinter.Grid.rowconfigure(self.frame2, l_row, weight=1)
      l_lab = ttk.Label(self.frame2, text='%d' % hour, width=10,
                        font=FONT14BOLD, background=LAB_BACKGROUND, anchor=tkinter.CENTER)
      l_lab.grid(row=l_row, column=1, padx=3, pady=3, sticky=tkinter.N+tkinter.S)
    for court in range(NUM_COURTS):
      for hour in range(HOUR_START, HOUR_START+HOURS_PER_DAY):
        self.all_buttons.append(ReservationButton(self, court+1, hour))

  def do_update_mainframe(self):
    """ update the main frame
    """
    self.last_udpate_time = datetime.now()
    l_allreserved = set()
    if self.current_date in self.reserved_hours:
      for l_tczhour in self.reserved_hours[self.current_date]:
        cbindex = (int(l_tczhour['tcz_court'])-1) * HOURS_PER_DAY \
                  + int(l_tczhour['tcz_hour']) - HOUR_START
        #cbindex = (int(l_tczhour['tcz_court'])-1) + (int(l_tczhour['tcz_hour']) - HOUR_START) * NUM_COURTS
        # username = app.tczUsers.ídToName[l_tczhour['tcz_user']]
        #print(cbindex,l_tczhour['tcz_user'])
        self.all_buttons[cbindex].but.configure(text=name_to_text(self.user_id_to_name[l_tczhour['tcz_user']]))
        if l_tczhour['tcz_free']:
          self.all_buttons[cbindex].but.configure(background=BG_FREEHOUR)
        else:
          self.all_buttons[cbindex].but.configure(background=BG_OTHER)
        l_allreserved.add(cbindex)
    # now update all fields which should be free
    cbindex = 0
    for l_cb in self.all_buttons:
      # print('%s index=%d' % (l_cb.text,cbindex))
      if (l_cb.but.cget('text') != FREE_USER and cbindex not in l_allreserved):
        l_cb.but.configure(text=FREE_USER)
        l_cb.but.configure(background=BG_FREE)
      cbindex += 1

  def ui_make_footer(self):
    """ make the footer of the app
    """
    style = ttk.Style()
    style.configure('Refresh.TButton', font=FONT18NORMAL)
    self.tk_message.set('')
    self.lab_message = ttk.Label(self.frame3, textvariable=self.tk_message, font=FONT18NORMAL)
    self.but_refresh = ttk.Button(self.frame3, text='Aktualisieren',
                                  command=self.update_curr_hours,
                                  style='Refresh.TButton')
    self.lab_message.pack(expand=1, fill=tkinter.X, side=tkinter.LEFT)
    self.but_refresh.pack()

  def ui_make_user_window(self, i_super):
    """ make the user window
    """
    self.user_win = tkinter.Toplevel(self)
    self.user_win.wm_title("Wähle Mitglied")
    tframe = ttk.Frame(self.user_win)
    tframe.pack(expand=1, fill=tkinter.BOTH)
    if os.name != 'nt':
      self.user_win.attributes('-zoomed', True)  # maximize window
    # load the user list for normal or superusers
    if i_super:
      l_users = self.user_names_super
    else:
      l_users = self.user_names_norm
    l_namecount = len(l_users)
    l_columns = 7
    l_rows = int(math.ceil(l_namecount / l_columns))
    # configure the rows and columns to resize
    for l_col in range(l_columns):
      tkinter.Grid.columnconfigure(tframe, l_col, weight=1)
    for l_row in range(l_rows):
      tkinter.Grid.rowconfigure(tframe, l_row, weight=1)
    # build the labels for all usernames
    for l_row in range(l_rows):
      for l_col in range(l_columns):
        namind = l_row*l_columns + l_col
        # the last row is probably not filled to the end
        if namind < l_namecount:
          label = ttk.Label(tframe, width=20, text=l_users[namind],
                            font=FONT14BOLD, background='white')
          label.bind("<Button-1>", self.do_select_user)
          label.grid(row=l_row, column=l_col, padx=5, pady=5)

  def ui_make_user_super(self, event):
    """ make window for super users
    """
    self.ui_make_user_window(True)

  def ui_make_user_normal(self, event):
    """ make window for normal users
    """
    self.ui_make_user_window(False)

  def do_select_user(self, event):
    """ update the user with the selected one
    """
    self.user_name = event.widget.cget('text')
    self.but_user.configure(text=self.user_name)
    self.user_win.destroy()

  def do_date_prev(self):
    """ move one day back
    """
    self.current_date = self.current_date + timedelta(days=-1)
    self.tk_datename.set(get_date_text(self.current_date))
    self.curr_date_name = get_date_name(self.current_date)
    self.do_update_mainframe()

  def do_date_next(self):
    """ move one day forward
    """
    self.current_date = self.current_date + timedelta(days=1)
    self.tk_datename.set(get_date_text(self.current_date))
    self.curr_date_name = get_date_name(self.current_date)
    self.do_update_mainframe()

  def do_date_today(self, update=True):
    """ move to the current date
    """
    self.current_date = date.today()
    self.tk_datename.set(get_date_text(self.current_date))
    self.curr_date_name = get_date_name(self.current_date)
    if update:
      self.do_update_mainframe()

# ---------------------------------------------------------------------
class MainWindow:
  """ build the main window
  """
  def __init__(self):
    self.tk_tk = tkinter.Tk()
    self.tk_tk.protocol("WM_DELETE_WINDOW", self.do_destroy_main_window)
    self.tk_tk.wm_title("Tennisplatz Reservierung")
    if os.name != 'nt':
      # attributes only works for UNIX
      self.tk_tk.attributes('-zoomed', True)  # maximize window
    self.app = ReservationApp(self.tk_tk)
    self.app.pack(side="top", fill="both", expand=True)
    self.state = False
    self.tk_tk.bind("<F11>", self.toggle_fullscreen)
    self.tk_tk.bind("<Escape>", self.end_fullscreen)

  def do_destroy_main_window(self):
    """ destroy myself
    """
    if tkinter.messagebox.askokcancel("Beenden", "Programm beenden?"):
        self.app.timer.cancel()
        self.tk_tk.destroy()

  def toggle_fullscreen(self, event=None):
    """ toggle the fullscreen mode
    """
    self.state = not self.state  # Just toggling the boolean
    if os.name != 'nt':
      self.tk_tk.attributes("-fullscreen", self.state)
    return "break"

  def end_fullscreen(self, event=None):
    """ stop the full screen mode
    """
    self.state = False
    if os.name != 'nt':
      self.tk_tk.attributes("-fullscreen", False)
    return "break"

if __name__ == '__main__':
  MY_APP = MainWindow()
  MY_APP.tk_tk.mainloop()
