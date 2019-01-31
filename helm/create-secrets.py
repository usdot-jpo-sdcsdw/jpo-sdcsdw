#!/usr/bin/env python

import sys

import yaml
import argparse
import getpass
import subprocess

def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--namespace', dest='namespace', default=None)
    parser.add_argument('--jetty-keystore', dest='jetty_keystore_arg', required=True, metavar='value|@path')
    parser.add_argument('--jetty-keystore-password', dest='jetty_keystore_password_arg', default=None, metavar='value|@path')
    parser.add_argument('--credentials-db-password', dest='credentials_db_password_arg', default=None, metavar='value|@path')
    parser.add_argument('-f', dest='values_file_path', default='values.yaml', help='Path to values yaml to find keys and values from')
    parser.add_argument('--allow-delete', dest='allow_delete', action='store_true', help='Allow this tool to delete any existing secrets')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Print kubectl commands (WARNING: MAY DISPLAY SENSITIVE INFORMATION)')
    parser.add_argument('kubectl_args', nargs=argparse.REMAINDER)
    return parser

def prompt_get_or_load(name, value, path):
    if value is not None:
        return (value, None)
    elif path is not None:
        return (None, path)
    else:
        return (getpass.getpass("{name}>".format(name=name)), None)

def parse_value_path(name, arg):
    if arg is None or len(arg) == 0:
        value = None
        path = None
    elif arg[0] == '@':
        path = arg[1:]
        value = None
    else:
        value = arg
        path = None
    return (name, value, path)
        
def find_secret_name_key(yaml, path):
    obj = reduce(lambda obj,part: obj[part], path, yaml)
    return (obj.get('name'), obj.get('key'))

def parse_prompt_get_or_load(arg):
    (name, key, value, path) = parse_name_key_value(arg)
    contents = prompt_get_or_load(name, value, path)
    return (name, key, contents)

def add_to_secrets(map, name, key, contents):
    if name not in map:
        map[name] = []
    map[name].append((key, contents))
    return map

def parse_args(parser, raw_args):
    args = parser.parse_args(raw_args)
    inputs = [ (['ssl', 'jetty_keystore_secret'], 'Jetty Keystore', args.jetty_keystore_arg),
               (['ssl', 'jetty_keystore_password_secret'], 'Jetty Keystore Password', args.jetty_keystore_password_arg), 
               (['credentials_db', 'password_secret'], 'Credentials DB Password', args.credentials_db_password_arg) ]
    secrets = [ (path,parse_value_path(name, arg)) for path,name,arg in inputs]
    namespace = args.namespace
    kubectl_args = args.kubectl_args
    values_file_path = args.values_file_path
    debug = args.debug
    allow_delete = args.allow_delete
    return (namespace, secrets, values_file_path, kubectl_args, allow_delete, debug)

def make_kubectl_create_secret_from_args(key, contents):
    value,path = contents
    arg_name = 'from-file' if path is not None else ('from-literal' or '')
    arg_value = value or path or ''
    return '--{arg_name}={key}={arg_value}'.format(arg_name=arg_name,key=key,arg_value=arg_value)

def make_kubectl_create_secret_args(namespace, kubectl_args, name, map):
    namespace_args = ['--namespace', namespace] if namespace is not None else []
    create_secret_generic = ['create', 'secret', 'generic']
    name_arg = [name]
    from_args = [ make_kubectl_create_secret_from_args(key, contents) for key,contents in map ]
    return create_secret_generic + namespace_args + kubectl_args + name_arg + from_args

def make_kubectl_delete_secret_args(namespace, kubectl_args, name):
    namespace_args = ['--namespace', namespace] if namespace is not None else []
    delete_secret = ['delete', 'secret']
    name_arg = [name]
    return delete_secret + namespace_args + kubectl_args + name_arg

def do_kubectl_call(args):
    full_args = ['kubectl'] + args
    return subprocess.Popen(full_args, stdout=sys.stdout, stderr=sys.stderr).wait()

def main(argv):
    parser = make_parser()
    (namespace, secrets, values_file_path, kubectl_args, allow_delete, debug) = parse_args(parser, argv[1:])
    with open(values_file_path) as f:
        values_yaml = yaml.safe_load(f)
    processed_secrets = [ (find_secret_name_key(values_yaml, path),prompt_get_or_load(*parsed)) for path,parsed in secrets ]
    secrets_map = reduce(lambda map, secret: add_to_secrets(map, secret[0][0], secret[0][1], secret[1]), processed_secrets, {})
    if allow_delete:
        kubectl_delete_secret_args_list = [ make_kubectl_delete_secret_args(namespace, kubectl_args, name) for name,_ in secrets_map.items() ]
        if debug:
            print kubectl_delete_secret_args_list
        [ do_kubectl_call(kubectl_delete_secret_args) for kubectl_delete_secret_args in kubectl_delete_secret_args_list ]
    kubectl_create_secret_args_list = [ make_kubectl_create_secret_args(namespace, kubectl_args, name, map) for name,map in secrets_map.items() ]
    if debug:
        print kubectl_create_secret_args_list
    codes = [ do_kubectl_call(kubectl_create_secret_args) for kubectl_create_secret_args in kubectl_create_secret_args_list ]
    return reduce(lambda a,b: a or b, codes, 0)

if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)