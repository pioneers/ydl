Random Notes
=========================


Note that YDL operates on a many-to-many messaging model, so you can have several processes listen on the same channel if needed. This might be useful for logging; you can have a logging process listen to all your channels, without changing the behavior of your application at all.

A client may listen to any number of channels, as long as they're all passed as arguments to the constructor.

Clients will connect to the server in the ``Client()`` constructor; note that this will block if the server isn't available. Both ``send()`` and ``receive()`` will block and try to reconnect if the connection is lost.

If the server goes down, it may simply be restarted without too much chaos. Some messages may be lost if they were sent just before the server went down or just after it comes back up. This is somewhat unavoidable, so if you need to guarantee that a message was sent, you should implement confirmation messages. Actually, if you need that kind of guarantee, you should just use an industrial-strength solution like RabbitMQ or Apache Kafka.
