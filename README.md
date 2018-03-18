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

`cluster_venv`: Optional path to a python virtualenv in which the python
`shade` package is installed.

`cluster_auth_type`: Optional name of the OpenStack authentication plugin to
use.

`cluster_auth`: Optional dictionary containing authentication information.

`cluster_cloud`: Optional name of the OpenStack client config cloud name to use.

`cluster_state`: Desired state of the cluster, either `present` or `absent`.
The default value is `present`.

`cluster_name`: Name to give the Heat stack
It defaults to `cluster`

`cluster_environment_nodenet`: An environment file specifying the resource to
use for the per-node network, `Cluster:NodeNet`.

`cluster_environment_instance`: An environment file specifying the resource to
use for the instances, `Cluster:Instance`.

`cluster_environment`: A list of environment files to use when creating the
Heat stack.

`cluster_params`: Parameters that are passed in to the Heat stack.

  * `cluster_prefix`: Name prefix to use for instance hostname construction.

  * `cluster_groups`: JSON-structured list of node groups, each of which is
     described by a dict, containing the following:

    * `name`: A name to refer to this group
    * `flavor`: The name or UUID of an instance flavor to use for deploying this group.
    * `image`: The name or UUID of an image to use for deploying this group.
    * `user`: The name of a cloud user for which SSH keys have been provisioned and
      passwordless sudo has been configured.  Could be (for example), `centos`, `debian`
      or `ubuntu`.
    * `num_nodes`: The number of nodes to create within this group.
    * `volume_size`: Optional size in GB of volumes used to boot instances in
      this group when the `instance-w-volume.yaml` environment is used.
    * `volume_type`: Optional type of volumes used to boot instances in this
      group when the `instance-w-volume.yaml` environment is used.

  * `cluster_keypair`: Name of an SSH key pair to use to access the instances.

  * `cluster_az`: Name of the availability zone in which to create the
    instances.

  * `cluster_net`: JSON-structure list of networks, each of which is described
    by a dict, containing the following:

    * `net`: Name or UUID of a neutron network to attach the instances to.
    * `subnet`: Name or UUID of a neutron subnet to attach the instances to.
    * `security_groups`: Optional list of names or UUIDs of security groups to
      add the instances' ports to.
    * `floating_net`: Optional name or UUID of a neutron network to attach
      floating IPs to when the `nodenet-w-fip.yaml` environment is used.

`cluster_inventory`: After deployment, an inventory file is generated,
which can be used in subsequent Ansible-driven configuration.

`cluster_roles`: A set of group assignments to make in the Ansible inventory file
that is generated.  This parameter is a list of dicts of the form:

  * `name`: Name of the group to define in the Ansible inventory.
  * `groups`: A list of groups selected from the dict objects supplied to `cluster_groups`, above.

`cluster_group_vars`: A dictionary mapping inventory groups to group variables
to be defined for that group. The group variables for each group are defined as
a dictionary mapping variable names to their values.

Dependencies
------------

This role depends on the python `shade` package being installed on the target
host. The package may be installed in a python virtual environment, in which
case the path to the virtualenv should be specified in the `cluster_venv`
variable.

The [stackhpc.os-shade](https://galaxy.ansible.com/stackhpc/os-shade/) role may
be used to install the python `shade` package.

Example Playbook
----------------

The following playbook creates a Heat stack for a cluster containing a `login`
group and a `compute` group.

    ---
    # This playbook uses the Ansible OpenStack modules to create a cluster
    # using a number of baremetal compute node instances, and configure it
    # for a SLURM partition
    - hosts: openstack
      roles:
        - role: stackhpc.cluster-infra
          cluster_name: "openhpc"
          cluster_params:
            cluster_prefix: "ohpc"
            cluster_keypair: "admin_rsa"
            cluster_net:
              - net: "internal"
                subnet: "internal"
            cluster_groups:
              - name: "login"
                flavor: "compute-B"
                image: "CentOS7-OpenHPC"
                num_nodes: 1
              - name: "compute"
                flavor: "compute-A"
                image: "CentOS7-OpenHPC"
                num_nodes: 16
          cluster_group_vars:
            cluster:
              ansible_user: centos

Author Information
------------------

- Stig Telfer (<stig@stackhpc.com>)
