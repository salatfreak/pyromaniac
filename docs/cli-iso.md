---
parent: Command Line Interface
nav_order: 20
---

# ISO Generation
*Pyromaniac* supports compiling your configuration and embedding it into an
*ISO* image with a single command. You can produce images for both live boots
and unattended installation. Just like *Ignition* code, *ISO* images will be
written directly to the standard output and need to be redirected into a file.

To create a live image from your configuration, simply add the `--iso`
parameter as in `pyromaniac --iso . > image.iso`.

To make the *ISO* image automatically install *Fedora CoreOS* according to 
your configuration instead of booting a live image, specify a target disk using
the `--iso-disk` parameter as in `pyromaniac --iso --iso-disk /dev/sda . >
image.iso`.

## Finetuning Your Image
You can use the `--iso-arch` parameter to generate an *ISO* for a processor
architechture other than *x86_64*. The list of supported architectures can be
[found on the *Fedora CoreOS* website][archs].

If you need static IP addressing in your live image or during installation, you
can use the `--iso-net` parameter. It accepts a comma-separated list of
*KEY=VALUE* pairs. The keys are the names of the fields to the *ip* kernel
parameter as [described in the Linux kernel documentation][ip] but with the
"-ip" suffixes removed. You may e.g. configure the IP address, netmask, gateway
and *DNS* server by adding `--iso-net
client=192.168.0.10,netmask=255.255.255.0,gw=192.168.0.1,dns0=9.9.9.9`
to your *Pyromaniac* command. When using your image as an installer, this
network configuration will NOT be adopted by the installed system. Use
*NetworkManager* configuration files for that.

You can specify custom parameters that will be passed through to the
[`coreos-installer iso customize` command][customize] by prefixing them with
`--iso-raw-`. You may e.g. add a kernel parameter to the destination system by
adding `--iso-raw-dest-karg-append quiet` to your *Pyromaniac* command.

[archs]: https://docs.fedoraproject.org/en-US/fedora-coreos/platforms/
[ip]: https://www.kernel.org/doc/Documentation/filesystems/nfs/nfsroot.txt
[customize]: https://coreos.github.io/coreos-installer/cmd/iso/#coreos-installer-iso-customize

## Image Caching
The *Fedora CoreOS* base images are downloaded to */data/cache*. The *Bash*
script will mount a persistent volume there to avoid downloading the entire
base image every time you generate a new image. If you don't use the *Bash*
script, you should persist that directory manually.
