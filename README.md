OpenStack Cluster-as-a-Service Infrastructure
=============================================

This role generates software-defined OpenStack infrastructure that can
be used for generating complex application topologies on demand.
A recent version of OpenStack Heat is used to achieve this.

Requirements
------------

The OpenStack APIs should be accessible from the target host.  OpenStack
Newton or later is required.  Client credentials should have been set
in the environment, or using the `clouds.yaml` format.

Role Variables
--------------

`cluster_name`: Name to give the Heat stack
It defaults to `cluster`

`cluster_params`: Parameters that are passed in to the Heat stack.

   `cluster_prefix`: Name prefix to use for instance hostname construction.
   `cluster_groups`: JSON-structured list of node groups, each of which is
     described by a dict, containing the following:

     `name`: A name to refer to this group
     `flavor`: The name or UUID of an instance flavor to use for deploying this group.
     `image`: The name or UUID of an image to use for deploying this group.
     `num_nodes`: The number of nodes to create within this group.

`cluster_inventory`: After deployment, an inventory file is generated,
which can be used in subsequent Ansible-driven configuration.

Dependencies
------------

Example Playbook
----------------

The following playbook generates a guest image and uploads it to OpenStack:

    ---
    # This playbook uses the Ansible OpenStack modules to create a cluster
    # using a number of baremetal compute node instances, and configure it
    # for a SLURM partition
    - hosts: openstack
      roles:
	- role: stackhpc.cluster_infra
	  cluster_name: "openhpc"
	  cluster_params:
	    cluster_prefix: "{{ cluster_name }}"
	    cluster_keypair: "{{ cluster_keypair }}"
	    cluster_groups: "{{ cluster_groups }}"
	    cluster_net: "{{ cluster_net }}"

    ---
    - name: Generate guest image and upload
      hosts: openstack
      roles:
        - role: stackhpc.os-image
          os_images_auth:
            auth_url:     "{{ lookup('env','OS_AUTH_URL') }}"
            username:     "{{ lookup('env','OS_USERNAME') }}"
            password:     "{{ lookup('env','OS_PASSWORD') }}"
            project_name: "{{ lookup('env','OS_TENANT_NAME') }}"
          os_images_list:
          - name: FedoraCore
            elements:
              - fedora
              - selinux-permissive
              - alaska-extras
            env:
              DIB_ALASKA_DELETE_REPO: "y"
              DIB_ALASKA_PKGLIST: "pam-python pam-keystone"

Author Information
------------------

- Stig Telfer (<stig@stackhpc.com>)
