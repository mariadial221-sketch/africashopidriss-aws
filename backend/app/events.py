"""Découplage : l'API publie un événement et rend la main immédiatement.
Les traitements lents (email, facture, notification vendeur) sont faits par un worker
abonné via SNS -> SQS -> Lambda. Si le worker tombe, les messages attendent dans la file."""
import json
import logging

from .config import settings

log = logging.getLogger("africashop.events")


def publish(event_type: str, payload: dict) -> None:
    body = {"type": event_type, **payload}
    if settings.events_mode == "sns" and settings.sns_topic_arn:
        import boto3

        boto3.client("sns", region_name=settings.aws_region).publish(
            TopicArn=settings.sns_topic_arn,
            Message=json.dumps(body, default=str),
            MessageAttributes={"event_type": {"DataType": "String", "StringValue": event_type}},
        )
    else:
        log.info("EVENT %s", json.dumps(body, default=str))
