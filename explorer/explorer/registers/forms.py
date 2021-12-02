from django.forms import ModelForm
from .models import Register



class RegisterForm(ModelForm):
	class Meta:
		model = Register
		fields = ['file_path', 'category', 'id_column', 'target_column']
		exclude = ('owner',)
