FROM quay.io/coreos/butane:release

RUN dnf5 install -y python3-pyyaml python3-jinja2 python3-pip
RUN pip install --no-cache-dir systemdunitparser

COPY entrypoint.sh /
COPY pyromaniac /src/pyromaniac

USER 1000:1000
WORKDIR /spec
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
