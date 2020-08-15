

def test_post_holtwinter(webapi):

    response = webapi.post_json(
        '/v1/forecast/holtwinter',
        {
            'input_data': [
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7,
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7,
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7,
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7
            ],
            'forecast_horizon': 12,
            'params': {

            }
        },
        headers={
            'Content-Type': "application/json",
        },
        status=200
    )

def test_post_holt(webapi):

    response = webapi.post_json(
        '/v1/forecast/holt',
        {
            'input_data': [
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7,
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7,
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7,
                8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7
            ],
            'forecast_horizon': 12,
            'params': {

            }
        },
        headers={
            'Content-Type': "application/json",
        },
        status=200
    )
