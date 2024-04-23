# get butane and coreos installer images
FROM quay.io/coreos/butane:v0.20.0 AS butane
FROM quay.io/coreos/coreos-installer:v0.21.0

# copy butane executable
COPY --from=butane /usr/local/bin/butane /usr/local/bin/butane

# install the python package installer
RUN dnf install -y /usr/bin/pip3 && dnf clean all

# install pyromaniac
COPY pyproject.toml README.md LICENSE /src/
RUN mkdir /src/pyromaniac && pip install --no-cache-dir --editable /src
COPY pyromaniac /src/pyromaniac/
COPY stdlib /usr/local/lib/pyromaniac

# set up environment
USER 1000:1000
VOLUME /spec /data/secrets /data/cache
EXPOSE 8000
WORKDIR /spec
ENTRYPOINT ["/usr/bin/python3", "-m", "pyromaniac"]
