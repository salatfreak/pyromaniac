---
parent: Command Line Interface
nav_order: 30
---

# HTTP(S) Server
*Pyromaniac* allows you to compile your configurations on demand and serve them
over HTTP(S). Simply add the `--serve` parameter to start an HTTP server on
the default *TCP* port 8000 as in `pyromaniac --serve .`.

Each time a client sends a GET request for the */config.ign* path, your
configuration will be compiled and sent back in the response body.

## Requesting Encryption Secrets
Besides the */config.ign* path, the server will also answer GET requests to
paths matching */+([a-z0-9-]).secret* by querying you in the terminal.

This way you don't need to write encryption keys or secret tokens into your
configurations or to your installation media but instead let the installer
request them while setting up the system. You can then paste them into the
terminal you are running *Pyromaniac* in e.g. from your password manager.

## Customizing Scheme and Address
You can specify the host and optionally the scheme and port using the
`--address` parameter as in `pyromaniac --server
--address https://192.168.0.10:4433`. The scheme will default to *HTTPS*, the
host to *127.0.0.1* and the port to 80 for *HTTP*, 443 for *HTTPS*, and 8000 if
the `--address` parameter is not specified.

The scheme determines whether the server will use *TLS* but it will always
listen on port 8000 on all interfaces. The host and port will only be used for
generating a TLS certificate and authentication credentials as described
in the next section. The `--address` parameter can also be used to embed the
appropriate remote address when generating remote *ISO* images.

The *Bash* script will, however, honor the address's port and publish the
internal port 8000 to the specified port on the host on all interfaces. This
means that running `pyromaniac --serve --address https://localhost:1234 .`
will open the server up to your local network beyond the localhost on port 1234
and use a TLS certificate for the hostname *localhost*. Use a firewall on your
host to control who can make requests to the *Pyromaniac* server.

## Mutually Secured Connection
Setting `--address https://HOSTNAME:PORT` for a hostname and port your server
is reachable at will automatically encrypt and mutually authenticate the
connection between the installer and the *Pyromaniac* server for you. 

*Pyromaniac* will generate a self-signed *TLS* root certificate and a secret
key for authentication for that and persist them in */data/secrets* as soon as
they are first required.

When the server is started with *HTTPS* scheme, the root certificate will be
loaded and used to sign a certificate for the configured hostname. If the root
certificate is embedded into the remote ISO image and it reaches the server
under the specified hostname, it will successfully establish an encrypted
connection.

To authenticate the connection the other way around, the server can be
configured to require basic authentication credentials from the client before
answering any request. Use the `--auth` parameter to specify the credentials.
Pass *none* to disable authentication and *auto* to instruct *Pyromaniac* to
deterministically derive authentication credentials from the aforementioned
secret key, the scheme, host, and port using a cryptographic hash function. The
default is *none* for *HTTP* and *auto* for *HTTPS*.

## Generating the Remote ISO Image
*Pyromaniac* provides a function to generate the configuration to generate an
*ISO* image that loads the actual configuration via *HTTP(S)*. It is available
only to the main component as `remote.merge()`. It will take the `--address`
and `--auth` parameters into account and include the *TLS* root certificate, if
the address scheme is *HTTPS*.

To generate a remote installer simply execute `pyromaniac --address ADDR
--auth AUTH <<< '$remote.merge()$' > remote.iso` with appropriate values
for the *address* and *auth* parameters.

Check out the [Remote Configuration][recipe] recipe for an example of creating
a remote ISO and loading the configuration over HTTPS.

[recipe]: recipes-remote.md
