# -*- coding=utf-8 -*-
# author: yanyang.xie@thistech.com

import os
import json

from pykube_util import KubernetesOperation

def create_namespace(name):
    if kube_op.exist_namespace(name):
        print 'Namespace %s is existed' %(name)
    else:
        kube_op.create_namespace(name)
        print 'Namespace %s has been created' %(name)

def delete_rc(rc_json_file):
    json_obj = _read_json_file(rc_json_file)
    if kube_op.exists_rc(json_obj):
        rc = kube_op.get_rc(json_obj)
        print "RC existed. metadata: %s" %(rc.obj['metadata'])
        kube_op.delete_rc(json_obj)

def create_rc(rc_json_file):
    json_obj = _read_json_file(rc_json_file)
    if kube_op.exists_rc(json_obj):
        rc = kube_op.get_rc(json_obj)
        print "RC existed. metadata: %s" %(rc.obj['metadata'])
    else:
        kube_op.create_rc(json_obj)
        rc = kube_op.get_rc(json_obj)
        print "RC existed. metadata: %s" %(rc.obj['metadata'])

def get_rc(rc_json_file):
    json_obj = _read_json_file(rc_json_file)
    if kube_op.exists_rc(json_obj):
        rc = kube_op.get_rc(json_obj)
        print "RC existed. metadata: %s" %(rc.obj['metadata'])
        return rc
    else:
        print "RC is not existed."
        return None

def _read_json_file(json_file):
    if not os.path.exists(json_file):
        print 'Not found rc json file: %, please check' %(json_file)
        exit(1)
    
    with open(json_file) as f:
        json_obj = json.load(f)
        return json_obj

if __name__ == '__main__':
    url = 'http://52.74.134.64:8080'
    kube_op = KubernetesOperation(url)
    
    rc_json_file = 'demo/demo-rc.json'
    create_namespace('my-ns')
    
    delete_rc(rc_json_file)
    print get_rc(rc_json_file)
    
    import time
    time.sleep(10)
    create_rc(rc_json_file)
    
    