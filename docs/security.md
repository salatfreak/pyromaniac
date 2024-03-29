---
nav_order: 70
---

# Security Considerations
*Pyromaniac* was developed with security in mind. Since it supports the
execution of arbitrary code from configurations and has networking
capabilities, you should however be mindful about the inevitable security
implications of these features.

## Code Execution
*Pyromaniac* allows configurations to contain arbitrary code in *Python* code
blocks and *Jinja* templates. Any untrusted file with a *.pyro* extension or
that gets loaded as a *Jinja* template (e.g., via the family of *load*
components in the standard library) is therefore a potential threat.

If you execute *Pyromaniac* in a container and trust the security of your
kernel and container manager, your host should be protected. If executed
through the recommended [*Bash* script][script], the current working directory
will be mounted read-only into the container and should therefore be safe from
modifications as well. The script will, however, mount two named volumes into
the container to cache downloaded *ISO* images and the authentication secret.
A malicious configuration may be able to place a modified *ISO* base image in
the cache to infect future ISO images generated by *Pyromaniac*. You can
explicitly disable this cache by passing the `--no-cache` flag to the *Bash*
script.

[script]: https://github.com/salatfreak/pyromaniac/blob/main/pyromaniac.sh

## Networking
Using *HTTPS* combined with client authentication should protect you from
*MitM* attacks and data leaks, even when opening the server up to a public
network.

*Pyromaniac* does, however, use *Python*'s built-in *HTTP* server which is
officially [not recommended for production][server]. The [security concerns
described in its documentation][concerns] should not apply to *Pyromaniac*
though, which only uses a very limited set of its features.

If the HTTP(S) server gets invoked, the *Bash* script will instruct podman to
open the configured port on all interfaces independently of the hostname/IP
address specified using the `--address` parameter. The purpose of the hostname
in that parameter is only to generate a matching TLS certificate. You can
change this by either running the container image manually or adapting the
*Bash* script to only publish the port up to a specific network.

When exposing the server to an untrusted network, it is always advisable to
minimize the attack surface and restrict access as much as possible. Consider
choosing a random TCP port, configuring a firewall to restrict access to only
specific client hosts, and/or placing *Pyromaniac* behind a *VPN* or reverse
proxy if maximizing security is of the essence to you.

[server]: https://docs.python.org/3.11/library/http.server.html
[concerns]: https://docs.python.org/3.11/library/http.server.html#http-server-security

## Authentication Credentials
Authentication credentials are generated by calculating the *SHA256* hash over
the scheme, host, port, and a randomly generated but cached 256-bit secret.
There is no known method to reverse this hash function and thereby derive the
secret key.

Keep in mind though that the same combination of server scheme, host, and port
will always result in the same authentication credentials. If you publish one
*ISO* image or *Ignition* configuration containing the credentials for loading
a configuration from a specific scheme, host, and port, these credentials will
keep working if you open the server on the same address again in the future.

You can always specify custom credentials using the `--auth` parameter to avoid
the use of automatically generated ones.
