Role Name
=========

Provide a role to create VM on VMware Vcenter or standalone ESXi from a OVA file

Role Variables
--------------

	ovftool_path
	vcenter
	vcenter_user
	vcenter_password
	datacenter
	cluster
	datastore
	portgroup
	vm_name
	path_to_ova
	ova_file
	power_on
	ssl_verify
	vm_password_key
	vm_password
	props
	deployment_option
	ovf_network_name
	vcenter_folder

Role Requirements
-----------------

This role needs the "ovftool" binary available here:
    https://www.vmware.com/support/developer/ovf/

Example Playbook
----------------

To use in your playbook:
```
- name: Create OVA VM
  include_role:
    name: ovftool
  vars:
    ovftool_path: '/usr/bin'
    vcenter: 'my_esxi_host'
    vcenter_user: 'my_esxi_username'
    vcenter_password: 'my_esxi_password'
    datacenter: ''
    cluster: ''
    datastore: 'datastore1'
    portgroup: ''
    vm_name: 'my_new_vm'
    path_to_ova: '/tmp/'
    ova_file: 'test.ova'
    power_on: true
    ssl_verify: false
    ovf_network_name:
      ova_network1: 'my_esxi_network1'
      ova_network2: 'my_esxi_network1'
```

A URL can be used instead of a local path and file by setting the `path_to_ova` to the path portion of the URL.  For instance, updating the above example to use a URL looks something like this:

```
- name: Create OVA VM
  include_role:
    name: ovftool
  vars:
    ...
    ova_path: 'https://some.hostname.com/path/to/ova'
    ova_filename: 'ova_file.ova'
    ...
```

Additional debugging produced by the `ovftool` can be enabled bu adding the `debug_opts:` flag like this:
```
- name: Create OVA VM
  include_role:
    name: ovftool
  vars:
    ...
    debug_opts:
      logFile: 'ovftool-1.log'
      logLevel: 'verbose'
    ...
```

**NOTE:** Currently this will place the resulting log files in the directory the playbook is run when executed with `connection: local` set.
