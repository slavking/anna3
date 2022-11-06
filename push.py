import pusher
import config

pusher_client = pusher.Pusher(
    app_id='921445',
    key='6fdb5caf8dfd70d25132',
    secret='15cdf666b36b340441f5',
    cluster='eu',
    ssl=True
)

def push(data):
    pusher_client.trigger(config.board, 'message', data)