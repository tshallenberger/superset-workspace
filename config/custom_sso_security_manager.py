from superset.security import SupersetSecurityManager
import logging


class CustomSsoSecurityManager(SupersetSecurityManager):
    def oauth_user_info(self, provider, response=None):
        logging.debug("[AUTH] oauth2 provider: {0}.".format(provider))
        if provider == "okta":
            me = self.appbuilder.sm.oauth_remotes[provider].userinfo()
            logging.debug("[AUTH] userinfo: {0}".format(me))

            if me is None:
                return None
            else:
                return {
                    "name": me["name"],
                    "email": me["primary_email"],
                    "id": me["short_id"],
                    "username": me["short_id"],
                    "first_name": me["first_name"],
                    "last_name": me["last_name"],
                }
