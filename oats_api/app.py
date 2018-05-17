#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import time
from kafka import KafkaProducer
import json

app = Flask(__name__)

events = [
    {
        'id': 1,
        'type': u'API',
        'event_name': u'API',
        'host': u'None',
        'timestamp': u'Now',
        'severity': 1,

    }
]


@app.route('/oats/api/event', methods=['POST'])
def create_event():
    if not request.json or not 'host' in request.json:
        abort(400)
    event = {
        'type': request.json.get('type', 'api'),
        'event_name': 'API/' + request.json.get('event_name', 'default_api_event'),
        'host': request.json.get('host', 'no host provided'),
        'timestamp': request.json.get('timestamp', int(time.time())),
        'severity': request.json.get('severity', 7),
        'data': request.json.get('payload', {'data': 'no data provided'})
    }
    events.append(event)
    # TODO: Add Kafka produce
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send('oats-api', json.dumps(event))
    producer.flush()
    return jsonify({'event': event}), 201


@app.route('/oats/api/events', methods=['GET'])
def get_events():
    return jsonify({'events': events})


@app.route('/oats/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = [event for event in events if event['id'] == event_id]
    if len(event) == 0:
        abort(404)
    return jsonify({'event': event[0]})


@app.route('/oats/api/events/<int:event_id>', methods=['DELETE'])
def delete_task(event_id):
    event = [event for event in events if event['id'] == event_id]
    if len(event) == 0:
        abort(404)
    events.remove(event[0])
    return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)


