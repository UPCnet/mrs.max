from plone import api
from pas.plugins.preauth.interfaces import IPreauthTask
from pas.plugins.preauth.interfaces import IPreauthHelper

from zope.component import getUtility
from zope.interface import implements
from zope.component import adapts

from mrs.max.utilities import prettyResponse
from mrs.max.utilities import IMAXClient
from maxclient.client import BadUsernameOrPasswordError

import logging

logger = logging.getLogger('mrs.max')


def getToken(credentials, grant_type=None):
    user = credentials.get('login').lower()
    password = credentials.get('password')

    maxclient, settings = getUtility(IMAXClient)()
    try:
        token = maxclient.getToken(user, password)
        return token
    except BadUsernameOrPasswordError as error:
        logger.error('Invalid credentials for user "{}" on "{}"'.format(user, maxclient.oauth_server))
    except Exception as error:
        logger.error('Exception raised while getting token for user "{}" from "{}"'.format(user, maxclient.oauth_server))
        logger.error('{}: {}'.format(error.__class__.__name__, error.message))
    # An empty token is returned in an exception is raised
    return ''


class oauthTokenRetriever(object):
    implements(IPreauthTask)
    adapts(IPreauthHelper)

    def __init__(self, context):
        self.context = context

    def execute(self, credentials):
        user = credentials.get('login').lower()
        pm = api.portal.get_tool(name='portal_membership')
        member = pm.getMemberById(user)

        if user == "admin":
            return

        oauth_token = getToken(credentials)

        if oauth_token:
            logger.info('oAuth token set for user: %s ' % user)
        else:
            logger.warning('oAuth token NOT set for user: %s ' % user)

        member.setMemberProperties({'oauth_token': oauth_token})
        return


class maxUserCreator(object):
    implements(IPreauthTask)
    adapts(IPreauthHelper)

    def __init__(self, context):
        self.context = context

    def execute(self, credentials):
        user = credentials.get('login').lower()

        if user == "admin":
            return

        token = getToken(credentials)
        if token == '':
            logger.warning('MAX user not created, we don''t have a valid token')
            return

        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(user)
        maxclient.setToken(token)

        try:
            maxclient.people[user].post()

            if maxclient.last_response_code == 201:
                logger.info('MAX user created for user: %s' % user)
            elif maxclient.last_response_code == 200:
                logger.info('MAX user already created for user: {}'.format(user))
            else:
                logger.error('Error creating MAX user for user: {}. '.format(user))
                logger.error(prettyResponse(maxclient.last_response))

            # Temporarily subscribe always the user to the default context
            # July2014 - Victor: Disable automatic subscription to the default
            # context as it was proven to not be used anymore.
            # maxclient.setActor(user)
            # portal_url = api.portal.get().absolute_url()
            # maxclient.people[user].subscriptions.post(object_url=portal_url)

        except:
            logger.error('Could not contact with MAX server.')
            logger.error(prettyResponse(maxclient.last_response))
