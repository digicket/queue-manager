# Introduction
This repository provides a basic web server for accepting messages and writing to a queue. The requirements of which are
described below.
```shell
The service should expose a REST API endpoint to define the message contents
The service should write the message to an SQS Queue
Write a queue-processor service for the SQS Queue
The service reads messages from the queue
The service should ideally handle batching, concurrent processing, error conditions etc.
```

# Server
The server is written using FastAPI framework for the REST APIs.
## Installation
```shell
which python3 # verify you have python3 installed
virtualenv -p {python3/path} queue_manager
source queue_manager/bin/activate
pip install -r requirements.txt
```
OR use pipenv to manage the virtual environment

## Start server
```shell
python main.py server
```
Navigate to http://127.0.0.1/docs to see the docs.

## Functional Documentation
The server is built using the FastAPI framework.

The schemas are defined in:
[schemas](server/api/schemas/message.py)

The endpoints are defined in:
[endpoints](server/api/endpoints/message.py)

The library provides an interface to the queue. Default is AWS SQS. This is a singleton.
[libs](server/libs/queue/sqs.py)

Configurations are provided as environment variables. They are defined in:
[config](server/config.py)

# Worker (Queue Processor)
## Start worker 
```shell
python main.py worker
```
## Functional Documentation
The worker starts as a process with multiple threads waiting for work. When a message is available on the queue, a 
worker thread is invoked and a task is assigned. By default there are 10 threads in the pool.

[task_scheduler](worker/utils/task_scheduler.py) creates a pool of threads and allows to add tasks or check for free 
worker threads.

[threadpool](worker/utils/threadpool.py) runs the work assigned to the threads in the pool.

[message_processor](worker/message_processor.py) processes the individual message and places the MessageHandle for a 
successful message into the `completed_queue`.

[subscriber](worker/subscriber.py) starts the worker. It first cleans up any `message_handle`s in the `completed_queue` 
from previously recieved messages. This is to avoid duplicate processing. It then checks how many free worker threads
are available and fetches the equal number of messages from SQS. The maximum number of worker threads is 10, so, the
maximum number of messages which can be simultaneously processed is also 10. This is configurable using the
environment variable `MAX_THREADS`.

Once a batch of messages is received, the subscriber schedules the messages to be processed. It then goes back to
cleaning the completed messages and then to listening to receive more messages.

# Testing
## Unit testing
```shell
pip install pytest
pytest tests
```


# TODO:
Dockerize
BatchDelete message handles after processing.