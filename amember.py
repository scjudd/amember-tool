#!/usr/bin/env python

import urllib, urllib2, cookielib
import datetime, re

class Error(Exception):
    """ Base class for exceptions in this module. """
    pass

class LoginError(Error):
    """ Raised when a login operation fails. """

    def __init__(self, username):
        self.username = username
    def __str__(self):
        return repr("Error logging in as %s" % self.username)

class UserExistsError(Error):
    """ Raised when trying to create a username that already exists in the system. """

    def __init__(self, username):
        self.username = username
    def __str__(self):
        return repr("User '%s' already exists!" % self.username)

class UserUpdateError(Error):
    """ Raised when an error occurs in trying to update existing user information. """

    def __init__(self, member_id):
        self.member_id = member_id
    def __str__(self):
        return repr("Could not update user info for user '%s'!" % self.member_id)

class AmemberSession(object):
    """ An aMember Session """

    def __init__(self, url, username, password):
        self.url = url # TODO: add logic to chomp off trailing '/'.. make sure /admin/ in url..
        self.username = username
        self.password = password
        
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

    def login(self):
        """ Log in to aMember """

        url = '%s/index.php' % self.url
        data = {
            'login': self.username,
            'passwd': self.password,
            'do_login': '1',
        }
        request = urllib2.Request(url, urllib.urlencode(data))
        response = self.opener.open(request)

        # Raise an exception if login fails.
        if "PHPSESSID" not in response.read():
            raise LoginError(self.username)

    def logout(self):
        """ Log out of aMember """

        url = '%s/logout.php' % self.url
        response = self.opener.open(url)

    def add_user(self, first_name, last_name, email, phone, street, city, state, zipcode, country='US'):
        """ Add a user to aMember """

        username = ''.join([first_name[0].lower(), last_name.lower()])
        password = 'test123' # TODO: Add password generation

        url = '%s/users.php' % self.url
        data = {
            'member_id': '',
            'login': username,
            'pass': password,
            'email': email,
            'name_f': first_name,
            'name_l': last_name,
            'country': country,
            'street': street,
            'city': city,
            'state': state,
            'zip': zipcode,
            'phone': phone,
        }
        extra = {
            'unsubscribed': '0',
            'aff_param': '',
            'action': 'add_save'
        }
        request = urllib2.Request(url, urllib.urlencode(dict(data.items() + extra.items())))
        response = self.opener.open(request)

        # Raise an exception if the username already exists in aMember.
        html = response.read()
        if 'please choose another username' in html:
            raise UserExistsError(username)
        else:
            data['member_id'] = re.search('member_id=(\d{1,5})', html).group(1)
            return data

    def del_user(self, member_id):
        """ Remove a user from aMember based on the member_id """

        url = '%s/users.php' % self.url
        data = {
            'member_id': member_id,
            'action': 'delete',
            'confirm': ' Yes ',
        }
        response = self.opener.open(url, urllib.urlencode(data))

    def add_subscription(self, member_id, product_id, start_date, end_date):
        """ Add a subscription to a given member. """

        url = '%s/users.php' % self.url
        data = {
            'member_id': member_id,
            'product_id': product_id,
            'begin_dateMonth': str(start_date.month).rjust(2,'0'),
            'begin_dateDay': str(start_date.day).rjust(2,'0'),
            'begin_dateYear': str(start_date.year),
            'expire_dateMonth': str(end_date.month).rjust(2,'0'),
            'expire_dateDay': str(end_date.day).rjust(2,'0'),
            'expire_dateYear': str(end_date.year),
        }
        extra = {
            'receipt_id': 'manual',
            'paysys_id': 'free',
            'amount': '0',
            'completed': '1',
            'payment_id': '',
            'action': 'payment_add',
        }
        request = urllib2.Request(url, urllib.urlencode(dict(data.items() + extra.items())))
        response = self.opener.open(request)

        if "Member Info Updated" not in response.read():
            raise UserUpdateError(member_id)


if __name__ == '__main__':
    a = AmemberSession('http://iccaonline.net/amember/admin', 'admin', '')
    a.login()

    member_id = a.add_user('Testy', 'McTestington', 'spencercjudd@gmail.com', '123-456-7890', '123 Test St.', 'Testington', 'TX', '12345')['member_id']

    product_id = 4 # ICCA AACC Preferred Member
    start_date = datetime.date.today()
    end_date = start_date.replace(year=start_date.year+1)
    a.add_subscription(member_id, product_id, start_date, end_date)
    
    #a.del_user(member_id)

    a.logout()
