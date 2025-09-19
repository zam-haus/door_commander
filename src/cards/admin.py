from django.contrib import admin
from django.forms import ModelForm

from cards.models import Card, RegistrationTerminal


class CardForm(ModelForm):
    class Meta:
        model = Card
        fields = "__all__"


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    form = CardForm
    list_display = (Card.id.field.name, Card.owner.field.name, Card.created_at.field.name, Card.updated_at.field.name,
                    Card.last_used_at.field.name)


class RegistrationTerminalForm(ModelForm):
    class Meta:
        model = RegistrationTerminal
        fields = "__all__"


@admin.register(RegistrationTerminal)
class RegistrationTerminalAdmin(admin.ModelAdmin):
    form = RegistrationTerminalForm
    list_display = (
        RegistrationTerminal.id.field.name,
        RegistrationTerminal.created_at.field.name,
        RegistrationTerminal.updated_at.field.name,
    )
