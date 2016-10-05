# -*- coding: utf-8 -*-

from app import init_app

def run():
    config = dict(
        host = '0.0.0.0',
        port = 5000,
        debug=True,
    )
    init_app().run(**config)


if __name__ == '__main__':
    run()