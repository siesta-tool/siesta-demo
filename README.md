# SIESTA DEMO

This repository demonstrates how the entire SIESTA infrastructure can be deployed using docker
containers.

### Docker images
All necessary images are contained in the docker-compose.yml file, which are:

- Preprocess component
- Query Processor
- User Interface
- Database layer, utilizing either Object Storage System (OSS) or Apache Cassandra

All containers are connected to the same network in order to communicate internally.

In order to deploy the entire infrastructure run the following command from inside the root directory:
```bash 
docker-compose up -d
```
Note, that this will deploy S3 as a Database layer. The Cassandra container is simply commented out.

All images for the SIESTA infrastructure are available in DockerHub (https://hub.docker.com/u/mavroudo), along with 
descriptions about the different environmental variables. Additionally, there are instructions in each
repository that will enable anyone to build the images from scratch. 

#### Preprocessing
The original repository of the preprocessing component is https://github.com/mavroudo/SequenceDetectionPreprocess.
Specifically, the image that utilized for this demonstration corresponds to the release 2.2.0
(https://github.com/mavroudo/SequenceDetectionPreprocess/releases/tag/v2.2.0). 

#### Query Processor
The original repository of the Query Processor is https://github.com/mavroudo/SequenceDetectionQueryExecutor.
Specifically, the image that utilized for this demonstration corresponds to the release 2.1.0
(https://github.com/mavroudo/SequenceDetectionQueryExecutor/releases/tag/v2.1.0). 

#### User Interface
The original repository of the User Interface is https://github.com/cmoutafidis/siesta-ui.
The default base url for this one is set to localhost. Since React applications run in the user browser, the 
url cannot be set by environmental variables. However, if you wish to deploy the infrastructure to a server
you can set the urls for query and preprocessing by modifying the config.json file.

### Datasets
A testing event log can be found in the `/datasets` folder. This dataset has the extension .withTimestamp and it
is a custom representation of an event log containing the trace id and the follow by the events in each trace.
For each event, there is information about its event type and timestamp, which are separated by the delimiter **/delab/**.

SIESTA also supports event logs with the extension **.xes**, which are common in the 
Business Process Management community. In the demonstration we utilize the dataset from the Business Process Intelligence
Challenge 2017, which can be found here (https://data.4tu.nl/articles/dataset/BPI_Challenge_2017/12696884).

[Demo Video] (https://drive.google.com/file/d/1TzgwGuBD05qBT1cegLKHKJZmJt2DHQ3j/view?usp=sharing)
