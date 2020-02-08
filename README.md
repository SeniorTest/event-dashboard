# event-dashboard
Using [Dash](https://dash.plot.ly) to visualize events. Events are expected to be stored in [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html). 


## Motivation
Enable to see all send events at a glance, provide filtering and visualizations for the events.
Enhance data by adding information from other services, like a [Pact broker](https://docs.pact.io/getting_started/sharing_pacts).

## Idea
A consumer gets all Kafka events on a regular basis and writes them into elasticsearch (Note: consuming and writing of events is not part of this application!)
On consuming the callbacks for updating the diagrams are called, for example "lastUpdate". The diagrams are build using timeseries between lastCleared and lastUpdate, as well es the consumer group id.

# Overview

![](docs/component_diagram.png)

## Getting started

### Run it locally

#### Setup elasticsearch

In order to run the application locally, you need have an Elasticsearch instance running. For development and to get started, it is recommended to use the single node dockerized instance, as described [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
```
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.5.2

docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" --name elastic docker.elastic.co/elasticsearch/elasticsearch:7.5.2
``` 

#### Setup plantuml

[Plantuml](https://plantuml.com) is used to create sequence diagrams based on the events. Since the receiver of the event is not contained in the event, the information is added as target to the schema file.
In order to work properly please add plantuml.jar along app.py.

#### Setup app

It is recommended (but not necessary) to use a [virtual environment](https://virtualenv.pypa.io/en/latest/userguide.html) virtual environment. 
Checkout the repository and install all required module using command

```
pip install -r requirements.txt
```

Afterwards start the app using 

```
python app.py
```

The dashboard is then available [here](http://127.0.0.1:18550/event-monitor/) following the rule 
```
http://<host>:<port>/<url_base_pathname>

# see line: app = dash.Dash(server=server, url_base_pathname=url_base_path, external_stylesheets=[dbc.themes.BOOTSTRAP])
# with url_base_path = config.config['url_base_path']

```

In order to add some test data you can use the test in test_add_new_event.py.
Run
```
pytest -k test_add_new_event.py
```
which will add a new event to elasticsearch.

Afterwards you should see the event in the dashboard.

### Build docker image

Run command
```
docker build -t event_monitor .
```
to build a docker image.

### Run docker container
```
# if running against local elasticsearch
docker run -p 18850:80 -it event_monitor

# if running against dockerized elasticsearch
docker run -p 18850:80 -it --name dashboard --link=elastic:elastic event_monitor
```

The link in the second command is used to connect the dashboard container to the elasticsearch container. For more information please have a look [here](https://www.linode.com/docs/applications/containers/docker-container-communication/).

## User Guide

You can see all events which are available at elasticsearch.
![](docs/plain_events_numbered_inputs.png)

You can also filter the events by timestamp using the input fields marked with the red 1 and 2. At the moment it is required to use the same date format, since no conversion or verification is implemented.
To use the configured timestamps for filter please press button "Apply Filter" marked with the red 3. If you want to reset the filter you can click on button "Reset Filter" marked with the red 4. This removes the filter criteria and will return all events and also update the input fields (red 1 and 2) with the oldest and the youngest timestamp.

In addition to timestamp (backend) filtering you can use the (frontend) filter as shown in the next screenshot
![](docs/table_filter.png)

### Charts

The table data are used to display various diagrams, for example number of events.
The diagrams/charts get visible when clicking on the according buttons, like it can be seen here:

![](docs/number_of_events.PNG)

![](docs/timeseries.PNG)

## Schema validation
To validate the events jsonschema is used. An example schema file can be found in folder event_schemas. An updated schema definition can either be placed in the same folder or in can be posted using Rest. See folder
```
tests/e2e/test_post_schema.py
```
as reference. Using that api result in creating a new schema file with a timestamp. The app reads that file and stores its content in-memory, to speed up event validation.