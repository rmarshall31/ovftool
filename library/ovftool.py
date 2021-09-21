#!/usr/bin/python

__author__ = 'pacogomez'

import atexit
import ssl
import urllib
import json

import requests
from ansible.module_utils.basic import *
from pyVim import connect
from pyVmomi import vim


def connect_to_api(vchost, vc_user, vc_pwd):
    if hasattr(ssl, 'SSLContext'):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
    else:
        context = None
    if context:
        service_instance = connect.SmartConnect(host=vchost, user=vc_user, pwd=vc_pwd, sslContext=context)
    else:
        service_instance = connect.SmartConnect(host=vchost, user=vc_user, pwd=vc_pwd)
    atexit.register(connect.Disconnect, service_instance)
    return service_instance.RetrieveContent()


def get_all_objs(content, vimtype):
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj


def find_virtual_machine(content, vm_name):
    virtual_machines = get_all_objs(content, [vim.VirtualMachine])
    for vm in virtual_machines:
        if vm.name == vm_name:
            return vm
    return None


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ovftool_path=dict(required=True, type='str'),
            vcenter=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_password=dict(required=True, type='str', no_log=True),
            datacenter=dict(required=True, type='str'),
            cluster=dict(required=True, type='str'),
            datastore=dict(required=True, type='str'),
            ovf_network_name=dict(required=False, type='str'),
            debug_opts=dict(required=False, type='str'),
            portgroup=dict(required=True, type='str'),
            disk_mode=dict(required=False, type='str', default='thin'),
            path_to_ova=dict(required=True, type='str'),
            ova_file=dict(required=True, type='str'),
            vm_name=dict(required=True, type='str'),
            vm_password_key=dict(required=False, type='str', no_log=True),
            vm_password=dict(required=False, type='str', no_log=True),
            power_on=dict(required=False, type='bool', default=True),
            ssl_verify=dict(required=False, type='bool', default=True),
            props=dict(required=False, type='dict'),
            deployment_option=dict(required=False, type='str'),
            vcenter_folder=dict(required=False, type='str')
        ),
        supports_check_mode=True,
    )

    try:
        content = connect_to_api(module.params['vcenter'], module.params['vcenter_user'],
                                 module.params['vcenter_password'])
    except vim.fault.InvalidLogin:
        module.fail_json(msg='exception while connecting to vCenter, login failure, check username and password')
    except requests.exceptions.ConnectionError:
        module.fail_json(msg='exception while connecting to vCenter, check hostname, FQDN or IP')

    target_vm = find_virtual_machine(content, module.params['vm_name'])

    if target_vm:
        module.exit_json(msg='A VM with the name {} is already present'.format(module.params['vm_name']))

    ovftool_exec = '{}/ovftool'.format(module.params['ovftool_path'])
    ova_file = '{}/{}'.format(module.params['path_to_ova'], module.params['ova_file'])
    quoted_vcenter_user = urllib.quote(module.params['vcenter_user'])
    vi_string = 'vi://{}:{}@{}'.format(quoted_vcenter_user,
                                       urllib.quote(module.params['vcenter_password'], safe=''),
                                       module.params['vcenter'])
    if len(module.params['datacenter'].strip()) > 0:
        vi_string += '/{}/host/{}'.format(module.params['datacenter'], module.params['cluster'])
    command_tokens = [ovftool_exec]

    if module.params['power_on']:
        command_tokens.append('--powerOn')
    if not module.params['ssl_verify']:
        command_tokens.append('--noSSLVerify')
    command_tokens.extend([
        '--acceptAllEulas',
        '--skipManifestCheck',
        '--allowExtraConfig',
        '--diskMode={}'.format(module.params['disk_mode']),
        '--datastore={}'.format(module.params['datastore']),
        '--name={}'.format(module.params['vm_name']), ])

    if 'ovf_network_name' in module.params.keys() and module.params['ovf_network_name'] is not None and len(
                module.params['ovf_network_name']) > 0:
            try:
                d=json.loads(module.params['ovf_network_name'].replace("'", "\""))
                for key,network_item in d.iteritems():
                    command_tokens.append('--net:{}={}'.format(key, network_item))
            except ValueError, e:
                command_tokens.append('--net:{}={}'.format(module.params['ovf_network_name'], module.params['portgroup']))
    else:
        command_tokens.append('--network={}'.format(module.params['portgroup']))

    if module.params['props']:
        for key in module.params['props'].keys():
            command_tokens.append('--prop:{}={}'.format(key, module.params['props'][key]))
    if 'vm_password_key' in module.params and module.params['vm_password_key'] and 'vm_password' in module.params and \
            module.params['vm_password']:
        command_tokens.append('--prop:{}={}'.format(module.params['vm_password_key'], module.params['vm_password']))
    if 'deployment_option' in module.params:
        command_tokens.append('--deploymentOption={}'.format(module.params['deployment_option']))
    if 'vcenter_folder' in module.params and module.params['vcenter_folder'] is not None:
        command_tokens.append('--vmFolder={}'.format(module.params['vcenter_folder']))
    if 'debug_opts' in module.params.keys() and module.params['debug_opts'] is not None and len(module.params['debug_opts']) > 0:
        d=json.loads(module.params['debug_opts'].replace("'", "\""))
        for key,debug_item in d.iteritems():
            command_tokens.append('--X:{}={}'.format(key, debug_item))

    command_tokens.extend([ova_file, vi_string])

    ova_tool_result = module.run_command(command_tokens)

    if ova_tool_result[0] != 0:
        module.fail_json(msg='Failed to deploy OVA, error message from ovftool is: {}'.format(ova_tool_result[1]))

    module.exit_json(changed=True, ova_tool_result=ova_tool_result)


if __name__ == '__main__':
    main()
