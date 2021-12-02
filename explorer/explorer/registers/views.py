import pandas as pd

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .tools_feature_selection import prediction_flow, classification_flow
from .models import Register

#messages.add_message(request, messages.INFO, 'Hello world.')

@login_required
def load_dataset(request):
	contexto = 'algo'
	context = {'contexto': contexto}
	return render(request, 'registers/load_dataset.html', context)


@login_required
def process_dataset(request):
	MAXIMUM_CSV_SIZE = 3.0
	data = {}

	if request.method == "GET":
		return HttpResponseRedirect(reverse("registers:load_dataset"))

	if request.method == 'POST':
		csv_file = request.FILES['uploaded_file']

		if not csv_file.name.endswith('.csv'):
			messages.error(request,'File is not CSV type')
			return HttpResponseRedirect(reverse("registers:load_dataset"))

		# if file is too large, redirect
		if csv_file.size/(1000*1000) > MAXIMUM_CSV_SIZE:
			messages.error(
				request,
				"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),)
			)
			return HttpResponseRedirect(reverse("registers:load_dataset"))

		goal = request.POST['choice']
		id_column = request.POST['id_column'] # if empty it is an empty str
		target_column = request.POST['target_column']
		dataset = pd.read_csv(csv_file.temporary_file_path())

		if goal == 'prediction':
			scores = prediction_flow(id_column, target_column, dataset)
		elif goal == 'classification':
			scores = classification_flow(id_column, target_column, dataset)

	data = {'df': scores.to_html(), 'goal': goal}
	
	return render(request, 'registers/show_features.html', data)


@login_required
def my_datasets(request):
	registers = Register.objects.filter(owner=request.user)
	data = {'registers': registers}
	return render(request, 'registers/my_datasets.html', data)


@login_required
def register_detail(request, register_id):
	register = Register.objects.get(id=register_id)
	data = {'register': register}
	return render(request, 'registers/register_detail.html', data)
