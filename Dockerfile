FROM ubuntu:20.04
MAINTAINER Jeffrey Duda <jeff.duda@gmail.com>

RUN apt-get update && apt-get install -y \
  python3-pip git \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install numpy itk flywheel-sdk pandas

ENV FLYWHEEL=/flywheel/v0
RUN mkdir -p ${FLYWHEEL}

#COPY *.py ${FLYWHEEL}/.
#COPY *.csv ${FLYWHEEL}/.

RUN mkdir -p /apps/quants
RUN git clone https://github.com/ftdc-picsl/QuANTs.git /apps/quants/ && cd /apps/quants && git pull && git checkout c83b5a0
RUN pip3 install /apps/quants/python/quants


ENTRYPOINT ["python3 run.py"]
