# -*- coding: utf-8 -*-
"""Login middleware."""

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User

from account.accounts import Account
from account.models import BkUser


class LoginMiddleware(object):
    """Login middleware."""

    def process_view(self, request, view, args, kwargs):
        """process_view."""
        if getattr(view, 'login_exempt', False):
            return None
        username = request.user.username
        user = authenticate(request=request)
        if user:
            request.user = user
            if request.user.username != username:
                auth_login(request, user)
            return None

        account = Account()
        return account.redirect_login(request)
