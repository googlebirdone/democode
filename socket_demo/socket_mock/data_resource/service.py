#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/28 14:59
# @Author  : GuQingJun
# @Site    : 
# @File    : service.py
# @Software: PyCharm
from flask import Flask, request
from flask_restx import Resource, Api, Namespace
import jsonpath

app = Flask(__name__)
api = Api(app)

superior_ns = Namespace("superior", description="上级系统")
robot_ns = Namespace("robot", description="机器人系统")


@superior_ns.route("")
class Superior(Resource):

    def post(self):
        args = request.json
        print(args)
        msg_type = jsonpath.jsonpath(args, "$.Type")[0]
        return {"msg_type": msg_type}


@robot_ns.route("")
class Control(Resource):
    def post(self):
        args = request.json
        print(args)
        msg_type = jsonpath.jsonpath(args, "$.Type")[0]
        return {"msg_type": msg_type}


api.add_namespace(superior_ns, "/superior")
api.add_namespace(robot_ns, "/robot")
if __name__ == '__main__':
    app.run(debug=True, port=3307)
