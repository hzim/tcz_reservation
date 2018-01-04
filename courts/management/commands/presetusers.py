from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

import sys

class Command(BaseCommand):
  help = 'presets the User table'

  
  def handle(self, *args, **options):
    allUsers = set()
    
    def makeUserName(lastname,firstname) :
      # make username "Lastname Firstname" first letter uppercase
      l_lastname = lastname[0:1].upper() + lastname[1:]
      l_firstname = firstname[0:1].upper() + firstname[1:]
      return(l_lastname + ' ' + l_firstname)

    f = open('user_import_2017.csv', mode='r', encoding='iso8859-1')
    # skip headline
    line = next(f)
    for line in f:
      split_str = line.split(';')
      strip_str = list(map(str.strip,split_str))

      # delete users
      if (strip_str[3] == 'D'):
        lastname = strip_str[0].lower()
        firstname = strip_str[1].lower()
        email = strip_str[2]
        username = makeUserName(lastname,firstname)
        try:
          user = User.objects.get(username = username)
          user.delete()
          self.stdout.write(self.style.SUCCESS('user deleted "%s"' % username))
        except:
          pass
 
      # enter new users
      if (strip_str[3] == 'C'):
        lastname = strip_str[0].lower()
        firstname = strip_str[1].lower()
        email = strip_str[2]
        username = makeUserName(lastname,firstname)
        # check for unique user names
        if (username in allUsers) :
          self.stdout.write(self.style.SUCCESS('user already existing "%s"' % username))
        else:
          allUsers.add(username)
        # check if user already exists
        isNewUser = False
        try:
          isNewUser = not User.objects.filter(username = username).exists()
        except:
          pass
        try:
          if (isNewUser) :
            user = User.objects.create_user(username,
                                            email=email,
                                            password='tczellerndorf',
                                            first_name = firstname,
                                            last_name = lastname)
            self.stdout.write(self.style.SUCCESS('user created "%s"' % username))
        except:
          self.stdout.write(self.style.SUCCESS('error "%s"' % sys.exc_info()[0]))
      
      #enter super users
      if (strip_str[3] == 'S'):
        lastname = strip_str[0]
        firstname = ""
        email = ""
        username = lastname
        # check if user already exists
        isNewUser = False
        try:
          isNewUser = not User.objects.filter(username = username).exists()
        except:
          pass
        try:
          if (isNewUser) :
            user = User.objects.create_superuser(username,
                                                 email=email,
                                                 password='tc4zellerndorf',
                                                 first_name = firstname,
                                                 last_name = lastname)
            self.stdout.write(self.style.SUCCESS('superuser created "%s"' % username))
        except:
          self.stdout.write(self.style.SUCCESS('error "%s"' % sys.exc_info()[0]))
