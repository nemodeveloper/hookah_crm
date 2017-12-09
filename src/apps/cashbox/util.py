# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from src.base_components.middleware.request import get_current_user


class ProductSellRestrictionMixin:

    def check_sell_owner(self, sell):
        auth_user = get_current_user()
        if auth_user.is_superuser:
            return
        if sell.seller_id != auth_user.id:
            raise PermissionDenied()
