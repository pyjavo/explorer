from django.forms import ModelForm, Form, CharField, CheckboxInput
from .models import Register



class RegisterForm(ModelForm):
    class Meta:
        model = Register
        fields = ['file_path', 'category', 'id_column', 'target_column']
        exclude = ('owner',)


class ChooseColumnsDataframeForm(Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)

        counter = 1
        for question in questions:
            self.fields[question] = CharField(
                label=question,
                required=False,
                widget=CheckboxInput()
            )
            counter += 1
