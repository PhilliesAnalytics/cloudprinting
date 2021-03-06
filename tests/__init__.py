# coding: utf-8
from attest import assert_hook, Tests, raises
from cloudprinting import (delete_job, get_job, list_jobs, list_printers,
                           OAuth2, submit_job)
from os import environ
from os.path import dirname, join
import requests
from time import sleep


PRINTER_ID = environ.get('CP_PRINTER_ID', '__google__docs')
PDF = join(dirname(__file__), "test.pdf")
suite = Tests()
auth = OAuth2(client_id=environ['CP_CLIENT_ID'],
              client_secret=environ['CP_CLIENT_SECRET'],
              refresh_token=environ['CP_REFRESH_TOKEN'])


@suite.test
def oauth2_requires_argument_sets():
    with raises(TypeError):
        OAuth2()

    # these should be fine
    OAuth2(access_token="foo", token_type="bar")
    OAuth2(client_id="foo", client_secret="bar", refresh_token="baz")


@suite.test
def listing_printers():
    printers = list_printers(auth=auth)['printers']
    assert isinstance(printers, list)


@suite.test
def print_pdf():
    job = submit_job(PRINTER_ID, PDF, auth=auth)['job']
    assert isinstance(job, dict)

    timeout = 30
    delay = 5
    attempts = range(int(timeout / delay) + 1)

    try:
        for i in attempts:
            if i > 0:
                sleep(delay)
            latest = get_job(id=job['id'], auth=auth)
            if latest['status'] == 'DONE':
                break
        else:
            assert False, "Job got stuck on '%s'" % latest['status']
    finally:
        assert delete_job(job['id'], auth=auth)['success'] == True


@suite.test
def response_is_returned_on_remote_failures():
    r = submit_job("bogus", PDF)
    assert isinstance(r, requests.Response)

    r = delete_job("bogus")
    assert isinstance(r, requests.Response)

    r = list_jobs()
    assert isinstance(r, requests.Response)
