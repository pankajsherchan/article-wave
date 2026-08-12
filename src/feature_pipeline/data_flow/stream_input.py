import json
import time
from datetime import datetime
from typing import Generic, Iterable, TypeVar

from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition

from core.config import settings
from core.mq import RabbitMQConnection

DataT = TypeVar("DataT")
MessageT = TypeVar("MessageT")


class RabbitMQPartition(StatefulSourcePartition, Generic[DataT, MessageT]):
    def __init__(
        self,
        queue_name: str,
        resume_state: MessageT | None = None,
    ) -> None:
        self._in_flight_msg_ids = resume_state or set()
        self.queue_name = queue_name
        self.connection = RabbitMQConnection()
        self.connection.connect()
        self.channel = self.connection.get_channel()

    def next_batch(self) -> Iterable[DataT]:
        try:
            method_frame, header_frame, body = self.channel.basic_get(
                queue=self.queue_name,
                auto_ack=True,
            )
        except Exception:
            time.sleep(10)
            self.connection.connect()
            self.channel = self.connection.get_channel()
            return []

        if method_frame:
            message_id = method_frame.delivery_tag
            self._in_flight_msg_ids.add(message_id)
            return [json.loads(body)]

        return []

    def snapshot(self) -> MessageT:
        return self._in_flight_msg_ids

    def garbage_collect(self, state) -> None:
        closed_in_flight_msg_ids = state

        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)

    def close(self) -> None:
        self.channel.close()


class RabbitMQSource(FixedPartitionedSource):
    def list_parts(self) -> list[str]:
        return ["single partition"]

    def build_part(
        self,
        step_id: str,
        for_part: str,
        resume_state: MessageT | None = None,
    ) -> StatefulSourcePartition[DataT, MessageT]:
        return RabbitMQPartition(
            queue_name=settings.RABBITMQ_QUEUE_NAME,
            resume_state=resume_state,
        )
