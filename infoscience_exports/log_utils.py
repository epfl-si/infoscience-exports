import logging

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in,\
    user_logged_out


class LogMixin(object):
    """ Generic Mixin to add "self.logger"
    """
    @property
    def logger(self):
        name = '.'.join([self.__class__.__module__, self.__class__.__name__])

        return logging.getLogger(name)


class FormLoggingMixin(LogMixin):
    """ Log any Validation errors on forms
    """
    def add_error(self, field, error):
        super(FormLoggingMixin, self).add_error(field, error)

        if field:
            self.logger.info('Form error on field %s: %s', field, error)
        else:
            self.logger.info('Form error: %s', error)


# Log any user connecting or leaving
logger = logging.getLogger('infoscience_exports.user_activity')


@receiver(user_logged_in)
def on_login(sender, **kwargs):
    request = kwargs.get('request')
    user = kwargs.get('user')
    logger.info("A User has logged in. Request : %s. User : %s"
                % (request, user))


@receiver(user_logged_out)
def on_logged_out(sender, **kwargs):
    request = kwargs.get('request')
    user = kwargs.get('user')
    logger.info("A User has logged out. Request : %s. User : %s"
                % (request, user))


class LoggedModelAdminMixin(LogMixin):
    """ Log any change on admin model
    """
    def save_model(self, request, obj, form, change):
        modified_fields = []
        if obj.is_dirty():
            modified_fields = obj.get_dirty_fields()

        try:
            super(LoggedModelAdminMixin, self).save_model(request=request,
                                                          obj=obj,
                                                          form=form,
                                                          change=change)
        except:
            raise
        else:
            if modified_fields:
                self.logger.info("Django admin : changes in model %s,"
                                 " fields : %s"
                                 % (self.__class__,
                                    ", ".join(modified_fields)))
