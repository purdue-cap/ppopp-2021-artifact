FROM debian:buster
COPY ./scripts /scripts
RUN /scripts/prepare.sh

USER user
RUN /scripts/build_mona.sh
RUN /scripts/build_retreet.sh
WORKDIR /home/user
CMD /bin/bash
