#!flask/bin/python
# -*- coding:utf-8 -*-
from app import app,lbs

# app.run(debug=True)
app.run(host='192.168.31.181', port=80, debug=True, use_reloader=False)
