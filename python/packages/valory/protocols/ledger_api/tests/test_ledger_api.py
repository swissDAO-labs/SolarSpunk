# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022 Valory AG
#   Copyright 2018-2021 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Tests package for the 'valory/ledger_api' protocol."""
from abc import abstractmethod
from typing import Callable, Type
from unittest import mock

import pytest

from aea.common import Address
from aea.exceptions import AEAEnforceError
from aea.mail.base import Envelope
from aea.protocols.base import Message
from aea.protocols.dialogue.base import Dialogue as BaseDialogue
from aea.protocols.dialogue.base import DialogueLabel

from packages.valory.protocols.ledger_api import LedgerApiMessage, message
from packages.valory.protocols.ledger_api.custom_types import (
    Kwargs,
    SignedTransactions,
    State,
    Terms,
    TransactionDigests,
)
from packages.valory.protocols.ledger_api.dialogues import (
    LedgerApiDialogue,
    LedgerApiDialogues,
)
from packages.valory.protocols.ledger_api.message import (
    _default_logger as ledger_api_message_logger,
)


LEDGER_ID = "ethereum"
CONTRACT_ID = "contract_id_stub"
CALLABLE = "callable_stub"
CONTRACT_ADDRESS = "contract_address_stub"


def test_get_balance_serialization():
    """Test the serialization for 'get_balance' speech-act works."""
    msg = LedgerApiMessage(
        performative=LedgerApiMessage.Performative.GET_BALANCE,
        ledger_id="some_ledger_id",
        address="some_address",
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_get_state_serialization():
    """Test the serialization for 'get_state' speech-act works."""

    args = ("arg1", "arg2")
    kwargs = Kwargs({"key": "value"})

    assert str(kwargs) == "Kwargs: body={'key': 'value'}"

    msg = LedgerApiMessage(
        performative=LedgerApiMessage.Performative.GET_STATE,
        ledger_id="some_ledger_id",
        callable="some_function",
        args=args,
        kwargs=kwargs,
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_get_raw_transaction_serialization():
    """Test the serialization for 'get_raw_transaction' speech-act works."""
    terms_arg = LedgerApiMessage.Terms(
        ledger_id="some_ledger_id",
        sender_address="some_sender_address",
        counterparty_address="some_counterparty_address",
        amount_by_currency_id={"currency_id_1": 1},
        quantities_by_good_id={"good_id_1": -1, "good_id_2": -2},
        nonce="some_nonce",
        is_sender_payable_tx_fee=False,
        fee_by_currency_id={"currency_id_1": 1},
        is_strict=True,
    )
    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.GET_RAW_TRANSACTION,
        terms=terms_arg,
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_send_signed_transaction_serialization():
    """Test the serialization for 'send_signed_transaction' speech-act works."""
    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.SEND_SIGNED_TRANSACTION,
        signed_transaction=LedgerApiMessage.SignedTransaction(
            "some_ledger_id", {"body": "some_body"}
        ),
        kwargs=Kwargs({}),
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_get_transaction_receipt_serialization():
    """Test the serialization for 'get_transaction_receipt' speech-act works."""
    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.GET_TRANSACTION_RECEIPT,
        transaction_digest=LedgerApiMessage.TransactionDigest(
            "some_ledger_id", "some_body"
        ),
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_balance_serialization():
    """Test the serialization for 'balance' speech-act works."""
    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.BALANCE,
        ledger_id="some_ledger_id",
        balance=125,
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_state_serialization():
    """Test the serialization for 'state' speech-act works."""

    ledger_id = "some_ledger_id"
    state = State(ledger_id, {"key": "some_state"})

    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.STATE,
        ledger_id=ledger_id,
        state=state,
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_raw_transaction_serialization():
    """Test the serialization for 'raw_transaction' speech-act works."""
    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.RAW_TRANSACTION,
        raw_transaction=LedgerApiMessage.RawTransaction(
            "some_ledger_id", {"body": "some_body"}
        ),
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_transaction_digest_serialization():
    """Test the serialization for 'transaction_digest' speech-act works."""
    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.TRANSACTION_DIGEST,
        transaction_digest=LedgerApiMessage.TransactionDigest(
            "some_ledger_id", "some_body"
        ),
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_transaction_receipt_serialization():
    """Test the serialization for 'transaction_receipt' speech-act works."""
    msg = LedgerApiMessage(
        message_id=2,
        target=1,
        performative=LedgerApiMessage.Performative.TRANSACTION_RECEIPT,
        transaction_receipt=LedgerApiMessage.TransactionReceipt(
            "some_ledger_id", {"key": "some_receipt"}, {"key": "some_transaction"}
        ),
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_error_serialization():
    """Test the serialization for 'error' speech-act works."""
    msg = LedgerApiMessage(
        performative=LedgerApiMessage.Performative.ERROR,
        code=7,
        message="some_error_message",
        data=b"some_error_data",
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_performative_string_value() -> None:
    """Test the string value of the performatives."""
    assert (
        str(LedgerApiMessage.Performative.GET_BALANCE) == "get_balance"
    ), "The str value must be get_balance"
    assert (
        str(LedgerApiMessage.Performative.GET_RAW_TRANSACTION) == "get_raw_transaction"
    ), "The str value must be get_raw_transaction"
    assert (
        str(LedgerApiMessage.Performative.SEND_SIGNED_TRANSACTION)
        == "send_signed_transaction"
    ), "The str value must be send_signed_transaction"
    assert (
        str(LedgerApiMessage.Performative.GET_TRANSACTION_RECEIPT)
        == "get_transaction_receipt"
    ), "The str value must be get_transaction_receipt"
    assert (
        str(LedgerApiMessage.Performative.BALANCE) == "balance"
    ), "The str value must be balance"
    assert (
        str(LedgerApiMessage.Performative.RAW_TRANSACTION) == "raw_transaction"
    ), "The str value must be raw_transaction"
    assert (
        str(LedgerApiMessage.Performative.TRANSACTION_DIGEST) == "transaction_digest"
    ), "The str value must be transaction_digest"
    assert (
        str(LedgerApiMessage.Performative.TRANSACTION_RECEIPT) == "transaction_receipt"
    ), "The str value must be transaction_receipt"
    assert (
        str(LedgerApiMessage.Performative.ERROR) == "error"
    ), "The str value must be error"


def test_encoding_unknown_performative() -> None:
    """Test that we raise an exception when the performative is unknown during encoding."""
    msg = LedgerApiMessage(
        performative=LedgerApiMessage.Performative.GET_BALANCE,  # type: ignore
        ledger_id=LEDGER_ID,
        address="address",
    )

    with pytest.raises(ValueError, match="Performative not valid:"):
        with mock.patch.object(
            LedgerApiMessage.Performative, "__eq__", return_value=False
        ):
            LedgerApiMessage.serializer.encode(msg)


def test_decoding_unknown_performative() -> None:
    """Test that we raise an exception when the performative is unknown during encoding."""
    msg = LedgerApiMessage(
        performative=LedgerApiMessage.Performative.GET_BALANCE,  # type: ignore
        ledger_id=LEDGER_ID,
        address="address",
    )

    encoded_msg = LedgerApiMessage.serializer.encode(msg)
    with pytest.raises(ValueError, match="Performative not valid:"):
        with mock.patch.object(
            LedgerApiMessage.Performative, "__eq__", return_value=False
        ):
            LedgerApiMessage.serializer.decode(encoded_msg)


@mock.patch.object(
    message,
    "enforce",
    side_effect=AEAEnforceError("some error"),
)
def test_incorrect_message(
    mocked_enforce: Callable,  # pylint: disable=unused-argument
) -> None:
    """Test that we raise an exception when the message is incorrect."""
    with mock.patch.object(ledger_api_message_logger, "error") as mock_logger:
        LedgerApiMessage(
            message_id=1,
            dialogue_reference=(str(0), ""),
            target=0,
            performative=LedgerApiMessage.Performative.STATE,  # type: ignore
            ledger_id=LEDGER_ID,
            state=LedgerApiMessage.State("some_ledger_id", {}),
        )

        mock_logger.assert_any_call("some error")


def test_send_signed_transactions_serialization() -> None:
    """Test that the serialization for 'send_signed_transactions' works."""
    msg = LedgerApiMessage(
        performative=LedgerApiMessage.Performative.SEND_SIGNED_TRANSACTIONS,
        signed_transactions=SignedTransactions(
            ledger_id=LEDGER_ID, signed_transactions=[dict(), dict(), dict(), dict()]
        ),
        kwargs=Kwargs(body={}),
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


def test_transaction_digests_serialization() -> None:
    """Test that the serialization for 'transaction_digests' works."""
    msg = LedgerApiMessage(
        performative=LedgerApiMessage.Performative.TRANSACTION_DIGESTS,
        transaction_digests=TransactionDigests(
            ledger_id=LEDGER_ID, transaction_digests=["", "", "", ""]
        ),
    )
    msg.to = "receiver"
    envelope = Envelope(
        to=msg.to,
        sender="sender",
        message=msg,
    )
    envelope_bytes = envelope.encode()

    actual_envelope = Envelope.decode(envelope_bytes)
    expected_envelope = envelope
    assert expected_envelope.to == actual_envelope.to
    assert expected_envelope.sender == actual_envelope.sender
    assert (
        expected_envelope.protocol_specification_id
        == actual_envelope.protocol_specification_id
    )
    assert expected_envelope.message != actual_envelope.message

    actual_msg = LedgerApiMessage.serializer.decode(actual_envelope.message)
    actual_msg.to = actual_envelope.to
    actual_msg.sender = actual_envelope.sender
    expected_msg = msg
    assert expected_msg == actual_msg


class BaseTestMessageConstruction:
    """Base class to test message construction for the ABCI protocol."""

    ledger_id = LEDGER_ID
    address = "address_stub"
    contract_id = CONTRACT_ID
    callable_ = CALLABLE
    msg_class = LedgerApiMessage
    contract_address = CONTRACT_ADDRESS

    @abstractmethod
    def build_message(self) -> LedgerApiMessage:
        """Build the message to be used for testing."""

    def test_run(self) -> None:
        """Run the test."""
        msg = self.build_message()
        msg.to = "receiver"
        envelope = Envelope(to=msg.to, sender="sender", message=msg)
        envelope_bytes = envelope.encode()

        actual_envelope = Envelope.decode(envelope_bytes)
        expected_envelope = envelope

        assert expected_envelope.to == actual_envelope.to
        assert expected_envelope.sender == actual_envelope.sender
        assert (
            expected_envelope.protocol_specification_id
            == actual_envelope.protocol_specification_id
        )
        assert expected_envelope.message != actual_envelope.message

        actual_msg = self.msg_class.serializer.decode(actual_envelope.message_bytes)
        actual_msg.to = actual_envelope.to
        actual_msg.sender = actual_envelope.sender
        expected_msg = msg
        assert expected_msg == actual_msg

    @classmethod
    def _make_terms(cls) -> Terms:
        """Build a Terms object."""
        return LedgerApiMessage.Terms(
            ledger_id=cls.ledger_id,
            sender_address="sender_address",
            counterparty_address="counterparty_address",
            amount_by_currency_id={},
            quantities_by_good_id={},
            nonce="nonce_stub",
        )


class TestGetBalance(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_BALANCE,  # type: ignore
            ledger_id=self.ledger_id,
            address=self.address,
        )


class TestBalance(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        assert str(LedgerApiMessage.Kwargs({})) == "Kwargs: body={}"
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.BALANCE,  # type: ignore
            ledger_id=self.ledger_id,
            balance=0,
        )


class TestGetRawTransaction(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_RAW_TRANSACTION,  # type: ignore
            terms=self._make_terms(),
        )


class TestRawTransaction(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.RAW_TRANSACTION,  # type: ignore
            raw_transaction=LedgerApiMessage.RawTransaction(
                ledger_id=LEDGER_ID, body={}
            ),
        )


class TestSendSignedTransaction(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.SEND_SIGNED_TRANSACTION,  # type: ignore
            signed_transaction=LedgerApiMessage.SignedTransaction(
                ledger_id=self.ledger_id, body={}
            ),
            kwargs=Kwargs({}),
        )


class TestTransactionDigest(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.TRANSACTION_DIGEST,  # type: ignore
            transaction_digest=LedgerApiMessage.TransactionDigest(
                ledger_id=LEDGER_ID, body=""
            ),
        )


class TestGetTransactionReceipt(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_TRANSACTION_RECEIPT,  # type: ignore
            transaction_digest=LedgerApiMessage.TransactionDigest(
                ledger_id=LEDGER_ID, body=""
            ),
        )


class TestGetTransactionReceiptWithParams(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_TRANSACTION_RECEIPT,  # type: ignore
            transaction_digest=LedgerApiMessage.TransactionDigest(
                ledger_id=LEDGER_ID, body=""
            ),
            retry_timeout=3,
            retry_attempts=1,
        )


class TestTransactionReceipt(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.TRANSACTION_RECEIPT,  # type: ignore
            transaction_receipt=LedgerApiMessage.TransactionReceipt(
                ledger_id=LEDGER_ID, receipt={}, transaction={}
            ),
        )


class TestGetState(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.GET_STATE,  # type: ignore
            ledger_id=self.ledger_id,
            callable="cabllable",
            args=("",),
            kwargs=LedgerApiMessage.Kwargs({}),
        )


class TestState(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.STATE,  # type: ignore
            ledger_id=self.ledger_id,
            state=LedgerApiMessage.State(ledger_id=LEDGER_ID, body={}),
        )


class TestError(BaseTestMessageConstruction):
    """Test message."""

    def build_message(self) -> LedgerApiMessage:
        """Build the message."""
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.ERROR,  # type: ignore
            code=1,
            message="",
            data=b"",
        )


class AgentDialogue(LedgerApiDialogue):
    """The dialogue class maintains state of a dialogue and manages it."""

    def __init__(
        self,
        dialogue_label: DialogueLabel,
        self_address: Address,
        role: BaseDialogue.Role,
        message_class: Type[LedgerApiMessage],
    ) -> None:
        """
        Initialize a dialogue.

        :param dialogue_label: the identifier of the dialogue
        :param self_address: the address of the entity for whom this dialogue is maintained
        :param role: the role of the agent this dialogue is maintained for
        :param message_class: the message class
        """
        LedgerApiDialogue.__init__(
            self,
            dialogue_label=dialogue_label,
            self_address=self_address,
            role=role,
            message_class=message_class,
        )


class AgentDialogues(LedgerApiDialogues):
    """The dialogues class keeps track of all dialogues."""

    def __init__(self, self_address: Address) -> None:
        """
        Initialize dialogues.

        :param self_address: the address of the entity for whom this dialogue is maintained
        """

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message,  # pylint: disable=redefined-outer-name
            receiver_address: Address,
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message

            :param message: an incoming/outgoing first message
            :param receiver_address: the address of the receiving agent
            :return: The role of the agent
            """
            return LedgerApiDialogue.Role.AGENT

        LedgerApiDialogues.__init__(
            self,
            self_address=self_address,
            role_from_first_message=role_from_first_message,
            dialogue_class=AgentDialogue,
        )


class LedgerDialogue(LedgerApiDialogue):
    """The dialogue class maintains state of a dialogue and manages it."""

    def __init__(
        self,
        dialogue_label: DialogueLabel,
        self_address: Address,
        role: BaseDialogue.Role,
        message_class: Type[LedgerApiMessage],
    ) -> None:
        """
        Initialize a dialogue.

        :param dialogue_label: the identifier of the dialogue
        :param self_address: the address of the entity for whom this dialogue is maintained
        :param role: the role of the agent this dialogue is maintained for
        :param message_class: the message class
        """
        LedgerApiDialogue.__init__(
            self,
            dialogue_label=dialogue_label,
            self_address=self_address,
            role=role,
            message_class=message_class,
        )


class LedgerDialogues(LedgerApiDialogues):
    """The dialogues class keeps track of all dialogues."""

    def __init__(self, self_address: Address) -> None:
        """
        Initialize dialogues.

        :param self_address: the address of the entity for whom this dialogue is maintained
        """

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message,  # pylint: disable=redefined-outer-name
            receiver_address: Address,
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message

            :param message: an incoming/outgoing first message
            :param receiver_address: the address of the receiving agent
            :return: The role of the agent
            """
            return LedgerApiDialogue.Role.LEDGER

        LedgerApiDialogues.__init__(
            self,
            self_address=self_address,
            role_from_first_message=role_from_first_message,
            dialogue_class=LedgerDialogue,
        )


class TestDialogues:
    """Tests abci dialogues."""

    agent_addr: str
    ledger_addr: str
    agent_dialogues: AgentDialogues
    ledger_dialogues: LedgerDialogues

    @classmethod
    def setup_class(cls) -> None:
        """Set up the test."""
        cls.agent_addr = "agent address"
        cls.ledger_addr = "ledger address"
        cls.agent_dialogues = AgentDialogues(cls.agent_addr)
        cls.ledger_dialogues = LedgerDialogues(cls.ledger_addr)

    def test_create_self_initiated(self) -> None:
        """Test the self initialisation of a dialogue."""
        result = self.agent_dialogues._create_self_initiated(  # pylint: disable=protected-access
            dialogue_opponent_addr=self.ledger_addr,
            dialogue_reference=(str(0), ""),
            role=LedgerApiDialogue.Role.AGENT,
        )
        assert isinstance(result, LedgerApiDialogue)
        assert result.role == LedgerApiDialogue.Role.AGENT, "The role must be agent."

    def test_create_opponent_initiated(self) -> None:
        """Test the opponent initialisation of a dialogue."""
        result = self.agent_dialogues._create_opponent_initiated(  # pylint: disable=protected-access
            dialogue_opponent_addr=self.ledger_addr,
            dialogue_reference=(str(0), ""),
            role=LedgerApiDialogue.Role.AGENT,
        )
        assert isinstance(result, LedgerApiDialogue)
        assert result.role == LedgerApiDialogue.Role.AGENT, "The role must be agent."
