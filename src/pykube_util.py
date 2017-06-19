# -*- coding=utf-8 -*-
# author: yanyang.xie@thistech.com

import operator
import pykube
import time

class KubernetesOperation():
    def __init__(self, kube_master_url):
        self.api = pykube.HTTPClient(pykube.KubeConfig.from_url(kube_master_url))

    def create_namespace(self, name):
        '''
        Change the rc replicas number
        @param name: name of namespace
        '''
        
        json_obj = { 'apiVersion': 'v1', 'kind': 'Namespace',
                     'metadata': { 'name': '%s' % (name), 'labels': { 'name': '%s' % (name) } }
                    }
        pykube.Namespace(self.api, json_obj).create()
    
    def exist_namespace(self, name):
        '''
        Change the rc replicas number
        @param name: name of namespace
        '''
        
        json_obj = { 'apiVersion': 'v1', 'kind': 'Namespace',
                     'metadata': { 'name': '%s' % (name), 'labels': { 'name': '%s' % (name) } }
                    }
        return pykube.Namespace(self.api, json_obj).exists()
    
    def delete_namespace(self, name):
        '''
        Change the rc replicas number
        @param name: name of namespace
        '''
        json_obj = { 'apiVersion': 'v1', 'kind': 'Namespace',
                     'metadata': { 'name': '%s' % (name), 'labels': { 'name': '%s' % (name) } } 
                    }
        pykube.Namespace(self.api, json_obj).delete()
    
    def create_rc(self, json_obj):
        '''
        Change the rc replicas number
        @param json_obj: json data of rc
        '''
        pykube.ReplicationController(self.api, json_obj).create()
    
    def get_rc(self, json_obj):
        '''
        Get Kubernetes ReplicationController
        @param json_obj: json data of rc
        '''
        return pykube.ReplicationController(self.api, json_obj)
    
    def exists_rc(self, json_obj):
        return pykube.ReplicationController(self.api, json_obj).exists()
    
    def exists_rc_by_name(self, name, namespace='default'):
        rc = self.get_rc_by_name(name, namespace)
        return rc.exists()
    
    def watch_rc(self, json_obj):
        return pykube.ReplicationController(self.api, json_obj).watch()
    
    def watch_rc_by_name(self, name, namespace='default'):
        rc = self.get_rc_by_name(name, namespace)
        return rc.watch()
    
    def get_rc_by_name(self, name, namespace='default'):
        '''
        Get Kubernetes ReplicationController
        @param name: rc name
        @param namespace: rc namespace 
        '''
        obj = {"apiVersion": "v1", "kind": "ReplicationController",
                "metadata": {"name": "%s" % (name), "namespace": "%s" % (namespace), }
              }
        return pykube.ReplicationController(self.api, obj)
    
    def delete_rc(self, json_obj):
        '''
        Change the rc replicas number
        @param json_obj: json data of rc
        '''
        pykube.ReplicationController(self.api, json_obj).delete()
    
    def delete_rc_by_name(self, name, namespace):
        json_obj = {
            "apiVersion": "v1",
            "kind": "ReplicationController",
            "metadata": {
                "name": "%s" % name,
                "namespace": "%s" % namespace
            }
        }
        pykube.ReplicationController(self.api, json_obj).delete()
    
    def change_rc_replicas(self, name, number, namespace='default'):
        '''
        Change the rc replicas number
        @param name: rc name
        @param number: rc replica number
        @param namespace: rc namespace
        '''
        
        rc = self.get_rc_by_name(name, namespace)
        if rc is None:
            return False
        
        if type(number) is not int:
            return False
        
        try:
            rc.update()
            rc.replicas = number
            rc.update()
            return True
        except Exception, e:
            print e
            return False

    def get_pod_list(self, namespace=None, pod_label_selector={}, pod_status='ready'):
        '''
        Get Kubernetes pod list
        @param namespace: name space in Kubernetes
        @param pod_label_selector: take label 'app' for example: {"app__in": {"blackbox-exporter", "redis"}}
        @param pod_status: pod status in Kubernetes, such as 'ready, pending, ContainerCreating, Running'
        '''
        pods = pykube.Pod.objects(self.api)
        if len(pod_label_selector) > 0:
            pods = pods.filter(selector=pod_label_selector)
        
        if namespace is not None:
            pods = pods.filter(namespace=namespace)
        
        pods = filter(operator.attrgetter(pod_status), pods)
        return pods

if __name__ == '__main__':
    kube_master_url = 'http://52.74.134.64:8080'
    kube_op = KubernetesOperation(kube_master_url)
    
    rc_name = 'blackbox-exporter'
    rc_namespace = 'my-ns'
    selector_app_name = 'blackbox-exporter'
    
    print 'create rc namespace'
    try:
        kube_op.create_namespace(rc_namespace)
    except:
        pass
    
    obj = { 'apiVersion': 'v1',
              'kind': 'ReplicationController',
              'metadata': { 'name': '%s' % (rc_name),
                            'namespace':'%s' % (rc_namespace)},
              'spec': 
               { 'replicas': 2,
                 'selector': { 'app': '%s' % ('blackbox-exporter')},
                 'template': 
                  { 'metadata': 
                     { 'name': 'blackbox-exporter',
                       'labels': { 'app': '%s' % (selector_app_name)} },
                    'spec': 
                     { 'containers': 
                        [ { 'image': 'prom/blackbox-exporter',
                            'name': 'blackbox',
                            'ports': [ { 'containerPort': 9115, 'name': 'blackbox' } ] 
                            } ] 
                      } 
                   } 
                } 
           }
    
    print 'create rc'
    kube_op.create_rc(obj)
    time.sleep(10)
    rc = kube_op.get_rc_by_name(rc_name, namespace=rc_namespace)
    
    print 'get rc pod list'
    pod_label_selector = {"app__in": {selector_app_name, }}
    print kube_op.get_pod_list(namespace=rc_namespace, pod_label_selector=pod_label_selector)
    
    print 'change rc replicas number to 1'
    print kube_op.change_rc_replicas(rc_name, 1, namespace=rc_namespace)
    time.sleep(3)
    
    print 'get rc pod list'
    print kube_op.get_pod_list(namespace=rc_namespace, pod_label_selector=pod_label_selector)
    
    print 'delete rc'
    kube_op.delete_rc(obj)
    time.sleep(10)
    
    print 'delete rc_namespace'
    kube_op.delete_namespace(rc_namespace)
    
