# solace_cloud_inventory

If you have a Solace cloud account with more than just a few services, it is no fun to fill the inventory file manually.

Ansible has a concept of a "dynamic inventory plugin" - that is, the inventory "file" will be generated on the fly with some queries to the Solace Cloud API.

## Basic Usage

This description assumes, that you are able to use the ansible-solace-collection, that is: you have installed the collection and all requirements.

This description assumes, that you have a valid Solace cloud token available.

### Create inventory-config-yml file.

As a pointer to the inventory plugin, you need an inventory config file.

In the same directory as your playbooks live, create a yml file like this

```
---
# solace_cloud_inventory.yml

plugin: solace.pubsub_plus.solace_cloud_inventory
solace_cloud_api_token: eyxwww... <place here your Solace cloud token>
```

Check your inventory with:

```
ansible-inventory -i solace_cloud_inventory.yml --playbook-dir ./ --list
```

### Advanced examples
#### Solace cloud token as environment variable

If you dont want to put your Solace cloud token in a file on disk (and even worse : in a git repo), you could put the token in an environment variable SOLACE_CLOUD_TOKEN

```
---
# solace_cloud_inventory.yml

plugin: solace.pubsub_plus.solace_cloud_inventory
```

Check your inventory with:

```
SOLACE_CLOUD_TOKEN=eyxwwwxxxx ansible-inventory -i solace_cloud_inventory.yml --playbook-dir ./ --list
```

#### Restrict your inventory to a subset of services

You can restrict your inventory only to services, where the service name matches a (python) regular expression.

For example, if you have a naming scheme for services, where all Integration brokers start with "int-", you could use a config file like this:

```
---
# solace_cloud_inventory.yml

plugin: solace.pubsub_plus.solace_cloud_inventory
solace_cloud_api_token: eyxwww... <place here your Solace cloud token>
service_filter: "^int-"
```

Check your inventory with:

```
ansible-inventory -i solace_cloud_inventory.yml --playbook-dir ./ --list
```


