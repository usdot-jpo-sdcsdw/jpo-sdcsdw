#!/usr/bin/env python

import sys

import argparse
import getpass
import subprocess
import hashlib

CAS_DATABASE='cas'
USERS_TABLE='users'
USERNAME_COLUMN='username'
PASSWORD_HASH_COLUMN='password'
MYSQL_USER='root'
ASSUMED_POD_NAME='credentials-db-0'
MYSQL_COMMAND='mysql'

def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--namespace', dest='namespace', default=None)
    parser.add_argument('--credentials-db-password', dest='credentials_db_password_arg', default=None, metavar='value|@path')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Print kubectl commands (WARNING: MAY DISPLAY SENSITIVE INFORMATION)')
    parser.add_argument('--raw-password', dest='raw_password', action='store_true', help='Interpret the password argument as a password, not as an MD5 hash')
    parser.add_argument('--update', action='store_true', help='Update the user instead of adding them')
    parser.add_argument('username', type=str, help='Username to add')
    parser.add_argument('password', type=str, nargs='?', help='MD5 hash of password to add (or raw password, if the --raw-password flag is provided')
    return parser

def prompt_get_or_load(name, value, path):
    if value is not None:
        return value
    elif path is not None:
        with open(path) as f:
            return f.read()
    else:
        return getpass.getpass("{name}>".format(name=name))

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

def parse_args(parser, raw_args):
    args = parser.parse_args(raw_args)
    namespace = args.namespace
    debug = args.debug
    update = args.update
    hash_password = not args.raw_password
    username = args.username
    credentials_db_password_secret=parse_value_path('Credentials DB Password',args.credentials_db_password_arg)
    if hash_password and args.password is not None:
        password_secret = parse_value_path('User Password Hash', hashlib.md5(args.password).hexdigest())
    else:
        password_secret = parse_value_path('User Password',args.password)
    
    return (username, password_secret, credentials_db_password_secret, hash_password, update, namespace, debug)
    
    
def make_insert_query(username, password_hash):
    return "INSERT INTO {table} VALUES ('{username}', '{password_hash}');".format(
        table=USERS_TABLE,
        username=username,
        password_hash=password_hash)
    
def make_update_query(username, password_hash):
    return "UPDATE {table} SET {password_hash_column}='{password_hash}' WHERE {username_column}='{username}';".format(
        table=USERNAME_TABLE,
        username=username,
        password_hash=password_hash,
        username_column=USERNAME_COLUMN,
        password_hash_column=PASSWORD_HASH_COLUMN)
    
def make_kubectl_exec_args(namespace, query, credentials_db_password):
    namespace_args = ['--namespace', namespace] if namespace is not None else []
    exec_base = [ 'exec', '-it', ASSUMED_POD_NAME, MYSQL_COMMAND ]
    mysql_args = [ '--', '--user', 'root', '-p' + credentials_db_password, '-e', query, CAS_DATABASE ]
    return namespace_args + exec_base + mysql_args
    
def do_kubectl_call(args):
    full_args = ['kubectl'] + args
    return subprocess.Popen(full_args, stdout=sys.stdout, stderr=sys.stderr).wait()

def main(argv):
    parser = make_parser()
    (username, password_secret, credentials_db_password_secret, hash_password, update, namespace, debug) = parse_args(parser, argv[1:])
    if hash_password:
        password = prompt_get_or_load(*password_secret)
        password_hash = hashlib.md5(password).hexdigest()
    else:
        password_hash = prompt_get_or_load(*password_secret)
    credentials_db_password = prompt_get_or_load(*credentials_db_password_secret)
    
    if update:
        make_query = make_update_query
    else:
        make_query = make_insert_query
    query = make_query(username, password_hash)
    
    exec_args = make_kubectl_exec_args(namespace, query, credentials_db_password)
    
    if debug:
        print exec_args
    
    do_kubectl_call(exec_args)

if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)