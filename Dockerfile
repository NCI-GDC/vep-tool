FROM quay.io/jeremiahsavage/cdis_base

USER root

RUN apt-get update && apt-get install -y --force-yes \
    openjdk-8-jre-headless \
    python-dev \
    libpq-dev \
    python-psycopg2 \
    libwww-perl \
    libclass-dbi-perl \
    libarchive-zip-perl \
    libjson-perl \
    libfile-copy-recursive-perl \
    libmodule-build-perl \
    wget \
    unzip

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER ubuntu

ENV HOME /home/ubuntu

ENV vep-tool 0.1c

RUN mkdir -p ${HOME}/tools/
WORKDIR ${HOME}/tools/

# There are lots of issues with v84 install. To mitigate the problems
# we first download bioperl, unpack and add to perl lib.
RUN mkdir -p ${HOME}/tools/lib/
WORKDIR ${HOME}/tools/
RUN wget https://github.com/bioperl/bioperl-live/archive/release-1-6-924.zip \
    && unzip release-1-6-924.zip \
    && mv ${HOME}/tools/bioperl-live-release-1-6-924/Bio ${HOME}/tools/lib/ \
    && rm ${HOME}/tools/release-1-6-924.zip \
    && rm -rf ${HOME}/tools/bioperl-live-release-1-6-924
ENV PERL5LIB ${PERL5LIB}:${HOME}/tools/lib/

# Next, we install VEP, but we must remove the test directory before installing
# because something is wrong with the test cache.
WORKDIR ${HOME}/tools/
RUN wget https://github.com/Ensembl/ensembl-tools/archive/release/84.zip && unzip 84.zip && mv ensembl-tools-release-84 ensembl-tools && rm 84.zip
WORKDIR ${HOME}/tools/ensembl-tools/scripts/variant_effect_predictor/
RUN rm -rf ${HOME}/tools/ensembl-tools/scripts/variant_effect_predictor/t
RUN perl INSTALL.pl --AUTO a --TEST 0

ENV PATH ${PATH}:${HOME}/tools/ensembl-tools/scripts/variant_effect_predictor/

# Set htslib path
ENV PATH ${PATH}:${HOME}/tools/ensembl-tools/scripts/variant_effect_predictor/htslib/

# Add VEP plugins
WORKDIR ${HOME}/tools/
RUN mkdir -p ${HOME}/tools/vep-plugins/
ADD vep-plugins ${HOME}/tools/vep-plugins/

## Install tool
WORKDIR ${HOME}
RUN mkdir -p ${HOME}/tools/vep-tool
ADD vep-tool ${HOME}/tools/vep-tool/
ADD setup.* ${HOME}/tools/vep-tool/
ADD requirements.txt ${HOME}/tools/vep-tool/

RUN /bin/bash -c "source ${HOME}/.local/bin/virtualenvwrapper.sh \
    && source ~/.virtualenvs/p3/bin/activate \
    && cd ~/tools/vep-tool \
    && pip install -r ./requirements.txt"

WORKDIR ${HOME}
