import pandas as pd

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .tools_feature_selection import prediction_flow, classification_flow, save_to_csv
from .models import Register
from .forms import RegisterForm


@login_required
def load_dataset(request):
	if request.method == 'GET':
		formulario = RegisterForm()

	context = {
		'formulario': formulario,
    }
	return render(request, 'registers/load_dataset.html', context)


@login_required
def process_dataset(request):
	MAXIMUM_CSV_SIZE = 3.0
	data = {}

	if request.method == "GET":
		return HttpResponseRedirect(reverse("registers:load_dataset"))

	if request.method == 'POST':

		csv_file = request.FILES['file_path']

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

		formulario = RegisterForm(request.POST, request.FILES)

		if formulario.is_valid():
			new_register = formulario.save(commit=False)
			new_register.owner=request.user

			partial_name = new_register.file_path.name
			try:
				partial_name = partial_name.split('.csv')[0]
			except IndexError:
				new_register.file_name = new_register.file_path.name
			else:
				new_register.file_name = partial_name

			# Dataset is created before temporary_file_path is lost after save
			dataset = pd.read_csv(csv_file.temporary_file_path())

			category = request.POST['category']
			id_column = request.POST['id_column'] # if empty it is an empty str
			target_column = request.POST['target_column']

			if category.lower() == 'prediction':
				scores = prediction_flow(id_column, target_column, dataset)
			elif category.lower() == 'classification':
				scores, X_new, fit_x = classification_flow(id_column, target_column, dataset)
				new_df = save_to_csv(X_new, fit_x)
				new_register.new_dataset = new_df.to_json(orient='split')

			new_register.scores = scores.to_json(orient='split')
			new_register.save()

			messages.success(request, "Tu dataset ha sido creado satisfactoriamente.")

			data = {
				'scores': scores.to_html(),
				'category': category,
				'uuid': new_register.id
			}
	
	return render(request, 'registers/show_features.html', data)


@login_required
def my_datasets(request):
	registers = Register.objects.filter(owner=request.user)
	data = {'registers': registers}
	return render(request, 'registers/my_datasets.html', data)


@login_required
def register_detail(request, register_id):
	register = Register.objects.get(id=register_id)
	# Transform JSON to Dataframe
	scores = pd.read_json(register.scores, orient='split')
	data = {
		'scores': scores.to_html(),
		'register': register
	}
	return render(request, 'registers/register_detail.html', data)


@login_required
def download_new_dataset(request, register_id):
	'''
	View to generate new dataset from classification

	output: Downloadable CSV file
	'''
	register = Register.objects.get(id=register_id)

	# Transform JSON to Dataframe
	results = pd.read_json(register.new_dataset, orient='split')
	response = HttpResponse(content_type='text/csv')
	new_file_name = 'new_'+str(register.file_name)+'.csv'
	response['Content-Disposition'] = 'attachment; filename='+new_file_name

	results.to_csv(path_or_buf=response, float_format='%.3f')
	return response

# TODO: View from challenge 3
