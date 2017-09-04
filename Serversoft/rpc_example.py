import pika
import json
import asyncio
from threading import Thread

loop = asyncio.get_event_loop()
credentials = {'username':'apiuser@gmail.com', 'password':'apikey'}

class RPC_API_client(object):

    hostname = 'b.waviot.ru'  # or specify your address
    credentials = pika.PlainCredentials(**credentials)
    parameters = pika.ConnectionParameters(hostname, 5672, '/api', credentials)
    connection = pika.BlockingConnection(parameters)
    callback_queue = 'amq.rabbitmq.reply-to'
    processor_thread = None

    def __init__(self):
        self.channel = RPC_API_client.connection.channel()

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=RPC_API_client.callback_queue)

        self.response_queue = asyncio.Queue()

        if RPC_API_client.processor_thread is None:
            RPC_API_client.processor_thread = Thread(target=RPC_API_client.processor)
            RPC_API_client.processor_thread.start()

    def on_response(self, ch, method, props, body):
        self.response = body

    def call(self, request):

        self.channel.basic_publish(exchange='',
                                   routing_key='api.requests',
                                   properties=pika.BasicProperties(
                                       reply_to=RPC_API_client.callback_queue
                                   ),
                                   body=request)

    @staticmethod
    def processor():
        while 1:
            RPC_API_client.connection.process_data_events()


    async def json_request(self, request):
        self.call(json.dumps(request))
        return await json.loads(self.response_queue.get())


sample_request = {
    "module": "channels",
    "action": "create",
	"email": "waviotuser@gmail.com",
	"apikey": "waviotwaviotwaviot",
	"http": ["users_site.com/call_1"],
	"mqtt": ["queue_1", "queue_2"]
}


rpc_client = RPC_API_client()

response = rpc_client.json_request(json.dumps(sample_request))