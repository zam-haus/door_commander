from datetime import datetime, timedelta, UTC

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from icecream import ic
import logging

from cards.models import Card, RegistrationTerminal
from cards.mqtt import cardreader_mqtt
from wait_until import wait_until

log = logging.getLogger(__name__)


@login_required(login_url='/')  # TODO determine correct login URL
def home(request):
    if request.user.cards.filter(
            disabled=False,
            last_used_at__lt=datetime.now() - timedelta(days=30),
            created_at__lt=datetime.now() - timedelta(days=30),
    ).exists():
        messages.info(request, "Du hast lange nicht verwendete Karten. Bitte sperre oder lösche diese.")

    context = dict(
        cards=request.user.cards.order_by("created_at").all(),
        messages=messages.get_messages(request),
        can_register_card=_can_register_card(request.user),
    )
    return render(request, 'cards/index.html', context)


def _is_allowed_to_have_multiple_cards(user):
    """
    Check if the user is allowed to have multiple cards.
    This can be overridden in the future to allow for more complex logic.
    """
    return user.is_superuser


def _read_card(timeout=30):
    """
    Returns the card that was read by the registration terminal in the last timeout seconds.
    """
    card_read_event = None
    registration_terminal = RegistrationTerminal.objects.first()
    if not registration_terminal:
        log.warning("No registration terminal found")
        return None

    # Wait for MQTT message to arrive upon new connection, should be sent with retain=True
    card_read_event = cardreader_mqtt.get_last_card_read(registration_terminal.door.mqtt_id)

    if not card_read_event:
        return None

    if timeout and card_read_event.when < datetime.now(UTC) - timedelta(seconds=timeout):
        log.warning("Card read event is too old, ignoring it.")
        return None
    card = Card.objects.filter(secret_id=card_read_event.card_secret_id).first()
    if card:
        card.last_used_at = max(card.last_used_at, card_read_event.when)
    else:
        card = Card.objects.create(
            secret_id=card_read_event.card_secret_id,
            last_used_at=card_read_event.when,
        )
    card.save()
    return card


def _can_register_card(user):
    """
    Check if the user can register a new card.
    This can be overridden in the future to allow for more complex logic.
    """
    if not RegistrationTerminal.objects.exists():
        log.warning("No registration terminal found, cannot register cards.")
        return False
    return _is_allowed_to_have_multiple_cards(user) or not user.cards.exists()


def register(request):
    if not _can_register_card(request.user):
        messages.error(request, "Du kannst keine neuen Karten registrieren.")
        return redirect(home)

    card = _read_card()
    if card is None:
        messages.error(request,
                       "Karte konnte nicht gelesen werden. Bitte Karte erneut an das Lesegerät halten und Aktion wiederholen.")
        return redirect(home)

    if card.owner is not None:

        if card.owner == request.user:
            if card.disabled:
                card.disabled = False
                card.save()
                messages.success(request, "Karte wurde entsperrt")
            else:
                messages.info(request, "Karte ist bereits registriert und aktiv.")
        else:
            # TODO Karte sofort sperren?
            # Karte wird nicht auf den aktuellen Nutzer um-registriert, da Karten evtl. gegen Pfand ausgegeben wurden
            messages.error(request, "Karte ist bereits durch einen anderen Nutzer registriert.")
            return redirect(home)
    else:
        card.owner = request.user
        card.disabled = False
        card.save()
        messages.success(request, "Karte wurde registriert.")

    return redirect(home)


def disable_scan(request):
    card = _read_card()
    if card is None:
        messages.error(request,
                       "Karte konnte nicht gelesen werden. Bitte Karte erneut an das Lesegerät halten und Aktion wiederholen.")
        return redirect(home)
    card.disabled = True
    card.save()
    messages.success(request, "Karte wurde gesperrt.")
    return redirect(home)


def modify(request, card_id):
    card = Card.objects.get(id=card_id)
    if not card:
        return HttpResponse(status=404)
    if card.owner != request.user:
        return HttpResponse(status=403)
    match request.POST.get("action"):
        case "delete":
            card.owner = None
            card.disabled = False
            card.save()
            messages.warning(request, f"Karte {card_id} gelöscht.")
        case "disable":
            card.disabled = True
            card.save()
            messages.success(request, f"Karte {card_id} gesperrt.")

    return redirect(home)
