# About
OpenFaaS Python function example for the [OpenFaaS vCenter Connector](https://github.com/openfaas-incubator/vcenter-connector).

# Usage
## Requirements
These steps require a running [OpenFaaS](https://docs.openfaas.com/deployment/) and [vSphere (vCenter)](https://docs.vmware.com/en/VMware-vSphere/index.html) environment. Also, the [OpenFaaS vCenter Connector](https://github.com/openfaas-incubator/vcenter-connector) must set be up correctly before deploying this example.

## Deployment
### Supported `stack.yaml` parameters
Modify the function `stack.yaml` as per your environment:

- Either add the OpenFaaS `gateway: <URL|IP>` information under `provider` or `export` it as an environment variable used by `faas-cli`
- Modify environment variables:
  - VC    - FQDN/IP for vCenter
  - VCUSERNAME - Username to access vCenter
  - VCPASSWORD - Password to access vCenter
  - TAGURN   - Unique ID for the tag to be attached
- A key-value annotation defines which VM event should trigger the function
  - A list of VM events from vCenter can be found [here](https://code.vmware.com/doc/preview?id=4206#/doc/vim.event.VmEvent.html)
  - The `topic` key-value annotation uses `.` syntax, e.g. `VmPoweredOnEvent` maps to `vm.powered.on`

**Note:** OpenFaaS provides some useful [debugging](https://docs.openfaas.com/deployment/troubleshooting/) configured via environment variables `write_debug` and `read_debug`.
   
### How to retrieve the `TAGURN`
The `TAGURN` can be retrieved from the ID field in the object, e.g. with `govc`:

```bash
$ govc tags.info <tag>            # example uses "vmon" as the tag name
Name:           vmon
  ID:           urn:vmomi:InventoryServiceTag:4c57977e-27fa-4392-b344-0a90a502f524:GLOBAL
  Description:  VM powered on
  CategoryID:   urn:vmomi:InventoryServiceCategory:ee941e4d-56ce-4ebf-86ab-0f615828d585:GLOBAL
  UsedBy: []
```

Link to `govc`: https://github.com/vmware/govmomi/tree/master/govc

### Deploy the Function

```bash
$ faas-cli deploy -f stack.yml
Deploying: pytag-fn.

Deployed. 202 Accepted.
```

### Invoke the Function

If the event topic is `vm.powered.on` the function can be triggered via the vCenter Client UI or using `govc`:

```bash
$ govc vm.power -on '*'
```