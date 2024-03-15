---
parent: Recipes
nav_order: 40
---

# Remote Configuration
Serving your configurations over *HTTP(S)* has the great advantage that you
neither have to include any potentially secret configuration details for your
final system on your unencrypted installer media, nor do you need to create new
media when your configuration changes.

This page outlines the installation of an encrypted server with mutually
secured remote configuration loading.

The machine you run *Pyromaniac* on and the one you want the system to be
installed on need to share a network, and your firewall and *NAT*
configurations need to allow the target machine to open *TCP* connections
to a port on the machine running *Pyromaniac*. The shared network can be the
internet, but a more restricted one would be preferable to reduce the attack
surface. If your IT infrastructure allows it, you may even directly connect the
two machines using some network cable and static IP addressing.

## Installer Preparation
The first thing we need to do is create our *ISO* installer. You'll need to
know the disk device you want to install *CoreOS* to and your *Pyromaniac*
machine's address.

Assuming you would like to install to */dev/sda* and your *Pyromaniac* *HTTPS*
server will run on port *4433* at *192.168.0.10*, you can create your installer
in a single command:

```sh
pyromaniac --iso --iso-disk /dev/sda \
  --address 'https://192.168.0.10:4433/' \
  <<< '`remote.merge()`' > installer.iso
```

A self-signed certificate and random credentials for encryption and mutual
authentication will be embedded into the installer by default.

## Setting Up Disk Encryption
To use disk encryption in *CoreOS*, you'll need to use *Clevis* pinning as
[described in the CoreOS docs][luks]. You may still want to choose and store
the encryption keys for your root partition and further data partitions
yourself.

This configuration piece will encrypt your root partition with a key of your
choosing to demonstrate the retrieval of secret keys over *HTTP(S)*. This would
be more useful for persistent data partitions in practice. Consider using
*Clevis* pinning for the root partition instead as [described in the CoreOS
docs][luks]. The configuration described here will break unattended upgrades
because you'll need to manually type in the encryption key every time the
machine is rebooted.

```python
storage.luks[0]:
    name: root
    label: luks-root
    device: /dev/disk/by-partlabel/root
    key_file: `contents(remote.url / "root.secret", remote.headers)`
    wipe_volume: true
```

Remember that the `remote` variable will only be available in your main
component. If you configure storage in a separate component, you'll need to
pass the *URL* and headers as arguments to it.

[luks]: https://docs.fedoraproject.org/en-US/fedora-coreos/storage/#_encrypted_storage_luks

## Perform the Installation
You can now start the *Pyromaniac* *HTTPS* server with the same address used
for the *ISO* generation using the following command:

```sh
pyromaniac --serve --address 'https://192.168.0.10:4433/' .
```

If you boot your installer medium, it will request the */config.ign* path from
your server, which will compile your configuration and send it back to the
installer. During the storage setup, the installer will request the encryption
key from the */root.secret* path. *Pyromaniac* will prompt you for the secret
in the terminal and respond to the request with whatever line you type.

The installer might request your configuration multiple times during the
installation process, and it will be recompiled every time. You might run into
problems if your code is not deterministic and depends on randomness to compile
your configuration.

After the installation finishes, the server will be up and running as specified
in your configuration.

## Serving Static Configurations
You might already have a readily compiled *Ignition* file or don't want the
server to recompile your configuration every time if compilation takes a bit
longer.

You can easily serve an *Ignition* file named *config.ign* by writing a
one-liner using the `ignition.config.replace` field:

```sh
pyromaniac --serve --address 'https://192.168.0.10:4433/' \
  <<< 'ignition.config.replace: `contents(Path("config.ign"))`'
```

## For Debugging
Remote configuration loading can accelerate testing of your configs in virtual
machines as well. Start the installation as usual but make a snapshot right
before the configuration is loaded. You can then restore that snapshot whenever
you'd like to test a new version of your configuration and have the
provisioning of your machine happen within seconds.

Since the *HTTP(S)* server will recompile your configuration on every request,
you can simply keep it running while tinkering with your configs.
