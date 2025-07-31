import pandas as pd
from confluent_kafka import Consumer, KafkaException
from src.common.sources.base_source import DataSource

class KafkaSource(DataSource):
    def load(self):
        topic = self.config["topic"]
        conf = self.config.get("conf", {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'mygroup',
            'auto.offset.reset': 'earliest'
        })
        timeout = self.config.get("timeout", 10)  # seconds
        max_messages = self.config.get("max_messages", 1000)

        consumer = Consumer(conf)
        consumer.subscribe([topic])

        messages = []
        try:
            count = 0
            while count < max_messages:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    break  # No more messages in timeout period
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        break
                    else:
                        raise KafkaException(msg.error())
                messages.append(msg.value().decode('utf-8'))
                count += 1
        finally:
            consumer.close()

        # Convert list of JSON strings or CSV strings into DataFrame
        # Assuming JSON lines, you might need to adjust for your data format
        df = pd.read_json("\n".join(messages), lines=True)

        return df

    def generate_sample_table(self):
        sample_df = super().generate_sample_table()
        print("Kafka source does not support writing sample data.")
        return sample_df
