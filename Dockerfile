FROM python:3.6

COPY src /app/src
COPY tests /app/tests
COPY docs /app/docs
WORKDIR /app/src

ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y software-properties-common

RUN apt-get install -y default-jre-headless

RUN pip install dash
RUN pip install dash-core-components
RUN pip install dash-html-components
RUN pip install dash-renderer
RUN pip install dash-table
RUN pip install dash-daq==0.1.5
RUN pip install dash-bootstrap-components
RUN pip install elasticsearch
# todo: remove deprecation warnings to enable updating to version 1.0.x
RUN pip install pandas==0.25.1
RUN pip install requests
RUN pip install jsonschema
RUN python -m pip install gunicorn

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr
RUN export JAVA_HOME

CMD ["gunicorn", "-w 8", "-b :80", "app:server"]