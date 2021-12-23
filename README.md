Update Kibana IPs on Elasticsearch
==================================
This is the readme file for the Update Kibana IPs on Elasticsearch tool.

This tools automates the process of replacing outdated IPs in any Index Pattern fields of an elasticsearch deployment for updated ones.

Usage
-----
Run the tool with:
```{bash}
python updateip.py -ip [proper_ip] -old-ip [outdated_ip]
```
where:

- `ip`: is the correct IP and IP address of the elasticsearch deployment
- `old-ip`: is the outdated IP to be replaced by `ip`

Known Issues
------------
As of the present, the `script` field whiting the Index Patterns cannot be replaced automatically by this tool. The tool throws a warning whenever it encounters one of them and they must be replaced manually on Elasticsearch deployment website.