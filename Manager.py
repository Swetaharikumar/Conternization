# Container manager

import Consts as const
from flask import Flask, request, jsonify
import json
import os.path


manager = Flask(__name__)  # Creating the flask web server


def make_response(content, status_code):
    response = manager.response_class(
        response=content,
        status=status_code,
        mimetype='application/json'
    )
    return response


@manager.route('/config', methods=['POST'])
def config():

    if request.method == 'POST':

        config_data = request.get_json()

        if not config_data:
            response = make_response(None, 409)
            return response

        for items in const.needed_config:
            if items not in config_data.keys():
                response = make_response(None, 409)
                return response

        filename_part1 = config_data['name']
        filename_part2 = config_data['major']
        filename_part3 = config_data['minor']
        filename = filename_part1 + '-' + filename_part2 + '-' + filename_part3 + '.cfg'

        if os.path.isfile('configfiles/' + filename):
            response = make_response(None, 409)
            return response

        if not os.path.isdir('configfiles'):
            print("Dir made")
            os.mkdir('configfiles')
            os.mkdir('containers')

        old_name = filename
        filename = 'configfiles/' + filename

        with open(filename, 'w') as outfile:
            json.dump(config_data, outfile)

        const.config_files["files"].append(old_name)
        response = make_response(None, 200)
        return response

    else:
        response = make_response(None, 409)
        return response


@manager.route('/cfginfo', methods = ['GET'])
def config_info():

    if request.method == 'GET':
        data = const.config_files
        content = json.dumps(data)
        response = make_response(content, 200)

        return response


@manager.route('/launch', methods = ['POST'])
def launch():

    if request.method == 'POST':
        config_data = request.get_json()
        if not config_data:
            response = make_response(None, 409)
            return response

        filename_part1 = config_data['name']
        filename_part2 = config_data['major']
        filename_part3 = config_data['minor']
        filename = filename_part1 + '-' + filename_part2 + '-' + filename_part3 + '.cfg'

        if filename not in const.config_files["files"]:
            response = make_response(None, 404)
            return response

        return_dic = {}
        name = 'configfiles/' + filename
        instance_name = const.operation.launch_instance(name)
        return_dic["instance"] = instance_name
        return_dic["name"] = filename_part1
        return_dic["major"] = filename_part2
        return_dic["minor"] = filename_part3
        const.instance_info['instances'].append(return_dic)
        content = json.dumps(return_dic)
        response = make_response(content, 200)
        return response


@manager.route('/list', methods = ['GET'])
def list_instances():

    if request.method == 'GET':
        content = json.dumps(const.instance_info)
        response = make_response(content, 200)
        return response


@manager.route('/destroy/<instance_name>', methods=['DELETE'])
def destroy_instance(instance_name):

    # print(const.instance_info["instances"])
    # print(instance_name)
    # print("")
    for dic in const.instance_info['instances']:
        if dic["instance"] == instance_name:
            const.instance_info['instances'].remove(dic)
            const.operation.destroy_instance(instance_name)
            response = make_response(None, 200)
            return response

    response = make_response(None, 404)
    return response


@manager.route('/destroyall', methods = ['DELETE'])
def destroyall():

    for dic in const.instance_info['instances']:
        instance_name = dic["instance"]
        const.operation.destroy_instance(instance_name)

    const.instance_info['instances'] = []

    response = make_response(None, 200)
    return response



if __name__ == "__main__":
    manager.run(host='localhost', port=8080)
