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

Example Playbook
----------------

To use in your playbook:

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
