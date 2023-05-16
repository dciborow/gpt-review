"""Azure DevOps API incoming message handler."""
from __future__ import annotations

import os

import azure.functions as func

from gpt_review.repositories.devops import DevOpsFunction

HANDLER = DevOpsFunction(
    pat=os.environ["ADO_TOKEN"],
    org=os.environ["ADO_ORG"],
    project=os.environ["ADO_PROJECT"],
    repository_id=os.environ["ADO_REPO"],
)


def main(msg: func.ServiceBusMessage) -> None:
    """Handle an incoming message."""
    HANDLER.handle(msg)