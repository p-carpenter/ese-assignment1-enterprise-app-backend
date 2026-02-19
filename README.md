# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/p-carpenter/ese-assignment1-enterprise-app-backend/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                         |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------------- | -------: | -------: | ------: | --------: |
| manage.py                                    |       11 |        2 |     82% |     13-14 |
| musicplayer/\_\_init\_\_.py                  |        0 |        0 |    100% |           |
| musicplayer/admin.py                         |        0 |        0 |    100% |           |
| musicplayer/apps.py                          |        3 |        0 |    100% |           |
| musicplayer/migrations/0001\_initial.py      |        7 |        0 |    100% |           |
| musicplayer/migrations/\_\_init\_\_.py       |        0 |        0 |    100% |           |
| musicplayer/models.py                        |       32 |        2 |     94% |    18, 30 |
| musicplayer/permissions.py                   |        6 |        1 |     83% |        13 |
| musicplayer/serialisers.py                   |       31 |        0 |    100% |           |
| musicplayer/tests/\_\_init\_\_.py            |        0 |        0 |    100% |           |
| musicplayer/tests/test\_auth\_integration.py |       20 |        2 |     90% |    28, 39 |
| musicplayer/tests/test\_permissions.py       |       24 |        3 |     88% |     49-52 |
| musicplayer/urls.py                          |        8 |        0 |    100% |           |
| musicplayer/views.py                         |       39 |       14 |     64% |25, 35-36, 39, 44-57, 68, 71 |
| musicplayer\_project/\_\_init\_\_.py         |        0 |        0 |    100% |           |
| musicplayer\_project/asgi.py                 |        4 |        4 |      0% |     10-16 |
| musicplayer\_project/settings.py             |       48 |        2 |     96% |   37, 148 |
| musicplayer\_project/test\_Settings.py       |        4 |        0 |    100% |           |
| musicplayer\_project/urls.py                 |        4 |        0 |    100% |           |
| musicplayer\_project/wsgi.py                 |        4 |        4 |      0% |     10-16 |
| users/\_\_init\_\_.py                        |        0 |        0 |    100% |           |
| users/admin.py                               |        7 |        0 |    100% |           |
| users/apps.py                                |        3 |        0 |    100% |           |
| users/migrations/0001\_initial.py            |        8 |        0 |    100% |           |
| users/migrations/\_\_init\_\_.py             |        0 |        0 |    100% |           |
| users/models.py                              |        6 |        1 |     83% |        10 |
| users/tests.py                               |       17 |        0 |    100% |           |
| users/views.py                               |        0 |        0 |    100% |           |
| **TOTAL**                                    |  **286** |   **35** | **88%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/p-carpenter/ese-assignment1-enterprise-app-backend/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/p-carpenter/ese-assignment1-enterprise-app-backend/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/p-carpenter/ese-assignment1-enterprise-app-backend/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/p-carpenter/ese-assignment1-enterprise-app-backend/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fp-carpenter%2Fese-assignment1-enterprise-app-backend%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/p-carpenter/ese-assignment1-enterprise-app-backend/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.