#!/usr/bin/env python

import urllib, urllib2, cookielib
import re
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

USERNAME = 'admin'
PASSWORD = ''

# 1. Login

url = 'http://iccaonline.net/amember/admin/index.php'
data = 'passwd=%s&login=%s&do_login=1' % (PASSWORD, USERNAME)
req = urllib2.Request(url, data)
response = opener.open(req)

if "PHPSESSID" in response.read():
    print("Login successful!\n")
else:
    print("Login failed!")
    quit()


# 2. Enter POST loop

# Add Member
url = 'http://iccaonline.net/amember/admin/users.php'
user_data = {
    'member_id': '',
    'login': 'testtest',
    'pass': 'testtest',
    'email': 'test@test.com',
    'name_f': 'Testy',
    'name_l': 'McTestington',
    'country': 'US',
    'street': '123 Test St.',
    'city': 'Testington',
    'state': 'TX',
    'zip': '12345',
    'phone': '1234567890',

    'unsubscribed': '0',
    'aff_param': '',
    'action': 'add_save'
}
req = urllib2.Request(url, urllib.urlencode(user_data))
response = opener.open(req)

html = response.read()
if 'please choose another username' in html:
    print("Error! Username '%s' already taken!" % user_data['login'])
else:
    print("User '%s' successfully registered!" % user_data['login'])
    member_id = re.search('member_id=(\d{1,5})', html).group(1)

    # Add Subscription
    url = 'http://iccaonline.net/amember/admin/users.php'
    payment_data = {
        'receipt_id': 'manual',
        'amount': '0',
        'completed': '1',
        'payment_id': '',
        'member_id': member_id,
        'action': 'payment_add',

        'product_id': '4', # ICCA AACC Preferred Member
        'begin_dateMonth': '07',
        'begin_dateDay': '29',
        'begin_dateYear': '2011',
        'expire_dateMonth': '07',
        'expire_dateDay': '29',
        'expire_dateYear': '2012',
        'paysys_id': 'free',
    }
    req = urllib2.Request(url, urllib.urlencode(payment_data))
    response = opener.open(req)

    if "Member Info Updated" in response.read():
        print("Added payment info for '%s'!" % user_data['login'])
    else:
        print("Error updating payment info for '%s'!" % user_data['login'])


# Logout
url = 'http://iccaonline.net/amember/admin/logout.php'
response = opener.open(url)
