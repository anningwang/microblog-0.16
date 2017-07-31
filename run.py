#!flask/bin/python
# -*- coding:utf-8 -*-
from app import app

# app.run(debug=True)
if __name__ == '__main__':
    app.run(host='192.168.31.181', port=80, debug=True, use_reloader=False, threaded=True)
