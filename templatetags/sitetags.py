from django import template
from django.utils.translation import gettext
from django.conf import settings

from utils.time import datesince_days, dateuntil_days
from core.aai.signin import AAISignIn
from core import site_configs_manager as site_configs

register = template.Library()


@register.simple_tag
def use_kjy_signin():
    tpaa = getattr(settings, 'THIRD_PARTY_APP_AUTH', {})
    tpaas = getattr(settings, 'THIRD_PARTY_APP_AUTH_SECURITY', {})
    if 'SCIENCE_CLOUD' in tpaa and 'SCIENCE_CLOUD' in tpaas:
        name = tpaa['SCIENCE_CLOUD'].get('name', gettext('中国科技云通行证'))
        return name

    return None


@register.simple_tag
def get_aai_signin_name_url():
    tpaa = getattr(settings, 'THIRD_PARTY_APP_AUTH', {})
    tpaas = getattr(settings, 'THIRD_PARTY_APP_AUTH_SECURITY', {})
    if 'AAI' in tpaa and 'AAI' in tpaas:
        name = tpaa['AAI'].get('name', gettext('中国科技云身份认证联盟'))
        url = AAISignIn.get_signin_url()
        if url:
            return {'name': name, 'url': url}

    return None


@register.simple_tag(name='get_website_title')
def do_get_website_title():
    return site_configs.get_website_brand()


@register.simple_tag(name='get_website_url')
def do_get_website_url():
    u = site_configs.get_website_url()
    return u.rstrip('/')


def get_about_us():
    config = getattr(settings, 'WEBSITE_CONFIG', {})
    s = config.get('about_us')
    if not s:
        s = gettext('中国科学院计算机网络信息中心，科技云部。')

    return s


@register.simple_tag(name='get_about_us')
def do_get_about_us():
    return site_configs.get_about_us()


@register.filter("datesincedays", is_safe=False)
def datesince_days_filter(value, arg=None):
    """Format a date as the time since that date (i.e. "4 days")."""
    if not value:
        return ''
    try:
        if arg:
            days = datesince_days(value, arg)
        else:
            days = datesince_days(value)

        if days == 0:
            return gettext('今天 已过期')

        return gettext('已过期 %d天') % days
    except (ValueError, TypeError):
        return ''


@register.filter("dateuntildays", is_safe=False)
def dateuntil_days_filter(value, arg=None):
    """Format a date as the time until that date (i.e. "4 days")."""
    if not value:
        return ''
    try:
        days = dateuntil_days(value, arg)
        if days == 0:
            return gettext('今天 到期')

        return gettext('%d天 后到期') % days
    except (ValueError, TypeError):
        return ''
