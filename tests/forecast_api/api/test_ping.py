import falcon


def test_ping(webapi):
    response = webapi.get('/alert/ping')

    assert response.status == falcon.HTTP_OK
    assert response.body.decode('utf-8') == 'pong'
    assert response.headers['content-type'] == 'application/json'
