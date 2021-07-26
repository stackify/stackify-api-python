import json
import base64
from stackify import config

apm_installed = False

try:
    apm_installed = True
    from stackifyapm import insert_rum_script as insert_rum_script_apm
except ImportError:
    pass


def insert_rum_script():
    if apm_installed is True:
        return insert_rum_script_apm()

    rum_key = config.rum_key
    rum_script_url = config.rum_script_url

    if not rum_script_url or not rum_key:
        return None

    transaction_id = get_transaction_id()
    if not transaction_id:
        return None

    reporting_url = get_reporting_url()
    if not reporting_url:
        return None

    application_name = config.application
    if not application_name:
        return None

    environment = config.environment
    if not environment:
        return None

    settings = {
        "ID": transaction_id
    }

    if application_name:
        application_name_b64 = base64.b64encode(application_name.encode("utf-8")).decode("utf-8")
        if (application_name_b64):
            settings["Name"] = application_name_b64

    if environment:
        environment_b64 = base64.b64encode(environment.encode("utf-8")).decode("utf-8")
        if (environment_b64):
            settings["Env"] = environment_b64

    if reporting_url:
        reporting_url_b64 = base64.b64encode(reporting_url.encode("utf-8")).decode("utf-8")
        if (reporting_url_b64):
            settings["Trans"] = reporting_url_b64

    if not settings:
        return None

    return '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
        json.dumps(settings),
        rum_script_url,
        rum_key
    )


def get_transaction_id():
    return ''


def get_reporting_url():
    return ''
