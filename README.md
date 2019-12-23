# About
OpenFaaS Python function example for the [VMware Event Router](https://github.com/vmware-samples/vcenter-event-broker-appliance/vmware-event-router).

# Usage
## Requirements
These steps require a running environment with:

- [OpenFaaS](https://docs.openfaas.com/deployment/)
- [vSphere (vCenter)](https://docs.vmware.com/en/VMware-vSphere/index.html)
- [VMware Event Router](https://github.com/vmware-samples/vcenter-event-broker-appliance/vmware-event-router)

> **Note:** Alternatively, the [vCenter Event Broker Appliance](https://github.com/vmware-samples/vcenter-event-broker-appliance/) can be used to ease the deployment.

## Deployment
- Add the OpenFaaS `gateway: <URL or IP>` information under `provider` or `export` it as an environment variable used by `faas-cli` (`export OPENFAAS_URL=http://...`
  - The `faas-cli` documentation can be found [here](https://docs.openfaas.com/cli/install/)
- vCenter credentials and information about the tag ID and operation to be performed is stored in `vcconfig.toml`
  - This is for security reasons to not expose sensitive data
  - If you follow the steps below how to pass this information as a secret into OpenFaaS you only need to change the pre-defined key/value pairs in [vcconfig.toml](vcconfig.toml)
  - Please see [below](#how-to-retrieve-the-tagurn) how to retrieve the TAG URN parameter
- A key-value annotation under `topic` defines which VM event should trigger the function
  - A list of VM events from vCenter can be found [here](https://code.vmware.com/doc/preview?id=4206#/doc/vim.event.VmEvent.html)
  - Multiple topics can be specified using a `","`  delimiter, e.g. "`topic: "VmPoweredOnEvent,VmPoweredOffEvent"`"

**Note:** OpenFaaS provides some useful [debugging](https://docs.openfaas.com/deployment/troubleshooting/) configured via environment variables `write_debug` and `read_debug`.

Here's an example for `stack.yml`:

```yaml
provider:
  name: openfaas
  gateway: http://127.0.0.1:8080
functions:
  pytag-fn:
    lang: python3
    handler: ./pytag-fn
    image: embano1/pytag-fn:0.3
    environment:
      write_debug: true
      read_debug: true
    secrets:
      - vcconfig
    annotations:
      topic: VmPoweredOnEvent
```

Now create pass the vCenter and TAG information defined in `vcconfig.toml` into OpenFaaS as a secret:

```bash
# depending on your OpenFaaS requirement you might need to log into OpenFaaS before this step
$ faas-cli secret create vcconfig --from-file=vcconfig.toml
```

Next deploy the function:

```bash
$ faas deploy -f stack.yml
Deployed. 202 Accepted.
```

### How to retrieve the `TAG_URN`
The `TAG_URN` can be retrieved from the ID field in the object, e.g. with `govc`:

```bash
$ govc tags.info <tag>            # example uses "vmon" as the tag name
Name:           vmon
  ID:           urn:vmomi:InventoryServiceTag:4c57977e-27fa-4392-b344-0a90a502f524:GLOBAL
  Description:  VM powered on
  CategoryID:   urn:vmomi:InventoryServiceCategory:ee941e4d-56ce-4ebf-86ab-0f615828d585:GLOBAL
  UsedBy: []
```

Link to `govc`: https://github.com/vmware/govmomi/tree/master/govc

### Invoke the Function

If the event topic is `VmPoweredOnEvent` the function can be triggered via the vCenter Client UI or using `govc`:

```bash
# be careful as this wildcard will power on all VMs in your environment
$ govc vm.power -on '*'
```

# Development/Contributions (Python >=3.4)

After you've cloned the code you can easily create a virtual Python environment to make changes/contribute:

```bash
$ cd <cloned_directory>
$ python -m venv .
$ source bin/activate
$ pip install -r pytag-fn/requirements.txt
<make changes>
```

If you add new dependencies `pipreqs` is a useful tool to only reflect used packages in `requirements.txt`:

```bash
$ pipreqs --savepath ./pytag-fn/requirements.txt pytag-fn/
```

Read more about it [here](https://medium.com/python-pandemonium/better-python-dependency-and-package-management-b5d8ea29dff1).