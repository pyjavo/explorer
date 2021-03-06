import pandas as pd

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .tools_feature_selection import prediction_flow, classification_flow, save_to_csv
from .models import Register, AWSConstants
from .forms import RegisterForm, ChooseColumnsDataframeForm


MAXIMUM_CSV_SIZE = 3.0


@login_required
def load_dataset(request):
    if request.method == 'GET':
        formulario = RegisterForm()

    context = {
        'formulario': formulario,
        'MAXIMUM_CSV_SIZE': MAXIMUM_CSV_SIZE,
    }
    return render(request, 'registers/load_dataset.html', context)


@login_required
def process_dataset(request):
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
    registers = Register.objects.filter(owner=request.user, active=True)
    data = {'registers': registers}
    return render(request, 'registers/my_datasets.html', data)


@login_required
def register_detail(request, register_id):
    register = Register.objects.get(id=register_id)
    # Transform JSON to Dataframe
    scores = pd.read_json(register.scores, orient='split')

    # Build URL path for the read_csv method
    csv_path = register.file_path.url
    website_domain_url = request.META['HTTP_REFERER'].split('/registers')[0]
    columns_form = []  # TODO: delete if MEDIA files are managed

    if settings.DEBUG:
        # TODO: Implement AWS S3 to manage MEDIA files. Only works locally
        # MEDIA files are files uploaded by the user
        dataset = pd.read_csv(website_domain_url + csv_path)

        if request.method == 'GET':
            list_of_columns = dataset.columns.to_list()
            columns_form = ChooseColumnsDataframeForm(questions=list_of_columns)

        if request.method == 'POST':
            # Choose selected columns
            new_columns = []
            for key, value in request.POST.items():
                if key != 'csrfmiddlewaretoken':
                    new_columns.append(key)

            new_dataset = dataset[new_columns]

            # TODO: For larger CSV files, please check:
            # https://docs.djangoproject.com/en/3.2/howto/outputting-csv/#streaming-large-csv-files

            # return new CSV file
            response = HttpResponse(content_type='text/csv')
            new_file_name = 'new_'+str(register.file_name)+'.csv'
            response['Content-Disposition'] = 'attachment; filename='+new_file_name
            new_dataset.to_csv(path_or_buf=response, float_format='%.3f')
            return response

    data = {
        'scores': scores.to_html(),
        'register': register,
        'columns_form': columns_form,
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


# TODO: Check if works even if CORS or use origin link from cloud and a TemplateView
@login_required
def multivariate_analysis(request):

    constants = AWSConstants.objects.all()

    if not constants:
        messages.error(
            request,
            'Contact the administrator. AWS constants must be configured first to access.'
        )
        return HttpResponseRedirect(reverse("home"))

    data = {
        'albumBucketName': constants[0].album_bucket_name,
        'bucketRegion': constants[0].bucket_region,
        'IdentityPoolId': constants[0].identity_pool_id,
        'LambdaFunctionURL': constants[0].lambda_function_url,
    }
    return render(request, 'registers/multivariate_analysis.html', data)
