from five import grok
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite

from plone.registry.interfaces import IRegistry
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent

from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from Products.PluggableAuthService.interfaces.events \
    import IPrincipalCreatedEvent

from maxclient.rest import MaxClient
from mrs.max.utilities import IMAXClient, prettyResponse
from mrs.max.browser.controlpanel import IMAXUISettings

import logging
import plone.api
from plone import api


logger = logging.getLogger('mrs.max')


@grok.subscribe(IConfigurationChangedEvent)
def updateMAXUserInfo(event):
    """This subscriber will trigger when a user change his/her profile data."""
    # Bypass MAX update if user is admin
    if api.user.get_current().id == 'admin':
        return
    # Only execute if the event triggers on user profile data change
    if 'fullname' in event.data or 'twitter_username' in event.data:
        site = getSite()
        pm = getToolByName(site, "portal_membership")
        if pm.isAnonymousUser():  # the user has not logged in
            username = ''
            return
        else:
            username = api.user.get_current().id
        memberdata = pm.getMemberById(username)
        properties = dict(displayName=memberdata.getProperty('fullname', ''),
                          twitterUsername=memberdata.getProperty('twitter_username', '')
                          )

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IMAXUISettings, check=False)
        oauth_token = memberdata.getProperty('oauth_token', '')

        maxclient = MaxClient(url=settings.max_server, oauth_server=settings.oauth_server)
        maxclient.setActor(username)
        maxclient.setToken(oauth_token)

        maxclient.people[username].put(**properties)


@grok.subscribe(IConfigurationChangedEvent)
def updateOauthServerOnOsirisPASPlugin(event):
    """This subscriber will trigger when an admin updates the MAX settings."""

    if 'oauth_server' in event.data:
        portal = getSite()
        portal.acl_users.pasosiris.oauth_server = event.data['oauth_server']


@grok.subscribe(IPropertiedUser, IPrincipalCreatedEvent)
def createMAXUser(principal, event):
    """This subscriber will trigger when a user is created."""

    pid = 'mrs.max'
    qi_tool = plone.api.portal.get_tool(name='portal_quickinstaller')
    installed = [p['id'] for p in qi_tool.listInstalledProducts()]

    if pid in installed:
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        user = principal.getId()

        try:
            maxclient.people[user].post()

            if maxclient.last_response_code == 201:
                logger.info('MAX user created: %s' % user)
            elif maxclient.last_response_code == 200:
                logger.info('MAX user already created: {}'.format(user))
            else:
                logger.error('MAX Error creating user: {}. '.format(user))
                logger.error(prettyResponse(maxclient.last_response))
        except:
            logger.error('Could not contact with MAX server.')
            logger.error(prettyResponse(maxclient.last_response))
