FROM ubuntu:16.04

MAINTAINER Kyle Hernandez

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && apt-get install -y --force-yes \
        build-essential \
        libcgi-pm-perl \
        libwww-perl \
        libclass-dbi-perl \
        libarchive-extract-perl \
        libarchive-zip-perl \
        libjson-perl \
        libfile-copy-recursive-perl \
        libmodule-build-perl \
        wget \
        unzip \
        git \
        zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# There are lots of issues with v84 install. To mitigate the problems
# we first download bioperl, unpack and add to perl lib.
RUN mkdir -p /opt/lib/ \
    && cd /opt \
    && wget https://github.com/bioperl/bioperl-live/archive/release-1-6-924.zip \
    && unzip release-1-6-924.zip \
    && mv /opt/bioperl-live-release-1-6-924/Bio /opt/lib/ \
    && rm /opt/release-1-6-924.zip \
    && rm -rf /opt/bioperl-live-release-1-6-924
ENV PERL5LIB ${PERL5LIB}:/opt/lib/

# Next, we install VEP, but we must remove the test directory before installing
# because something is wrong with the test cache.
RUN cd /opt \
    && wget https://github.com/Ensembl/ensembl-tools/archive/release/84.zip \
    && unzip 84.zip \
    && mv ensembl-tools-release-84 ensembl-tools \
    && rm 84.zip \
    && cd /opt/ensembl-tools/scripts/variant_effect_predictor/ \
    && rm -rf /opt/ensembl-tools/scripts/variant_effect_predictor/t \
    && perl INSTALL.pl --AUTO a --TEST 0
ENV PATH ${PATH}:/opt/ensembl-tools/scripts/variant_effect_predictor/

# Set htslib path
ENV PATH ${PATH}:/opt/ensembl-tools/scripts/variant_effect_predictor/htslib/

# Add VEP plugins
RUN mkdir -p /opt/vep-plugins/
ADD vep-plugins /opt/vep-plugins/

WORKDIR /opt
