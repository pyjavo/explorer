'''
This funtions were developed by the students to successfully make feature selection
'''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.feature_selection import (
    VarianceThreshold,
    SelectKBest,
    SelectPercentile,
    r_regression,
    chi2
)
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import _VectorizerMixin
from sklearn.feature_selection._base import SelectorMixin
from sklearn.exceptions import NotFittedError


def get_feature_out(estimator, feature_in):
    """
    From https://stackoverflow.com/q/57528350/2142093
    """
    if hasattr(estimator,'get_feature_names'):
        if isinstance(estimator, _VectorizerMixin):
            # handling all vectorizers
            return [f'vec_{f}' \
                for f in estimator.get_feature_names()]
        else:
            return estimator.get_feature_names(feature_in)
    elif isinstance(estimator, SelectorMixin):
        return np.array(feature_in)[estimator.get_support()]
    else:
        return feature_in


def get_ct_feature_names(ct, X_train):
    '''
    author: handles all estimators, pipelines inside ColumnTransfomer (CT)
    - doesn't work when remainder =='passthrough'
    - which requires the input column names.

    name: 'cat' or 'num' according to our CT
    step: estimators from the CT like SimpleImputer, StandardScaler, etc 
    '''
    output_features = []

    for name, estimator, features in ct.transformers_:
        if name!='remainder':
            if isinstance(estimator, Pipeline):
                current_features = features
                for step in estimator:
                    try:
                        current_features = get_feature_out(step, current_features)
                    except NotFittedError as error:
                        # Avoids NotFittedError: This VarianceThreshold instance is not fitted yet. 
                        # Call 'fit' with appropriate arguments before using this estimator.
                        if isinstance(step, VarianceThreshold):
                            try:
                                step.fit(X_train) # VarianceThreshold.fit()
                            except ValueError:
                                print("No feature is strong enough to keep. Current features: ")
                        else:
                            raise NotFittedError(error)
                features_out = current_features
            else:
                features_out = get_feature_out(estimator, features)
            output_features.extend(features_out)
        elif estimator=='passthrough':
            output_features.extend(ct._feature_names_in[features])
                
    return output_features


def get_split_values(dataset, remove_columns, target, test_size=0.25):
    '''
    Include the target in the remove_columns argument
    '''
    y = dataset[target]
    X = dataset.drop(remove_columns,axis=1)

    X_train, X_test, y_train, y_test = train_test_split(
    	X, y, test_size=test_size,random_state=1
    )
    
    return X_train, X_test, y_train, y_test


def get_cat_num_cols(dataset, X_train):
    cat_cols = [i for i in X_train.columns if dataset.dtypes[i]=='object']
    num_cols = X_train._get_numeric_data().columns

    return cat_cols, num_cols


def get_df_selected_features(X_train, y_train, p_value, cat_cols, num_cols):
    '''
    Select best features

    output: Dataframe with filtered columns and another DataFrame with names of the columns
    '''
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('std_scaler', StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy="most_frequent")),
        ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)),  # solo funciona en el nuevo sklearn
        ('selector', VarianceThreshold(threshold=(p_value * (1 - p_value)))),
    ])

    
    full_preproc_pipeline = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("cat", cat_pipeline, cat_cols),
    ])
    
    pipe = Pipeline([
        ('preprocessor', full_preproc_pipeline),
        ('r_regression', SelectKBest(r_regression, k='all')),
    ])
    
    pipe.fit(X_train, y_train)
    X_pipe = pipe.transform(X_train)
    
    df_column = pd.DataFrame(
    	X_pipe,
        columns=get_ct_feature_names(full_preproc_pipeline, X_train)
    )
    column_names=pd.DataFrame(df_column.columns)
    # does not return p-values
    results = pd.DataFrame(pipe.named_steps['r_regression'].scores_)
    
    return results, column_names


def get_feature_scores(result_df, column_names, classif=False):

    if classif == True:
    	# for classification datasets
        column_names=pd.DataFrame(column_names)
        result_df = pd.DataFrame(result_df)

    scores=pd.concat([column_names,result_df], axis=1)
    scores.columns = ["Feature", "Scores"]

    return scores.sort_values(by=['Scores'], ascending=False)



def prediction_flow(id_column, target_column, dataset):
	'''
	Makes the feature selection for prediction datasets
	'''

	if id_column:
		remove_columns = [id_column, target_column]
	else:
		remove_columns = [target_column]

	X_train, X_test, y_train, y_test = get_split_values(
        dataset,
        remove_columns,
        target_column,
        test_size=0.25
    )
	cat_cols, num_cols = get_cat_num_cols(dataset, X_train)
	dataset_result, names = get_df_selected_features(
		X_train,
		y_train,
		0.2,
		cat_cols,
		num_cols
	)
	scores = get_feature_scores(dataset_result, names, classif=False)

	return scores


# Classification methods


def classif_get_split_values(X, y, train_size):
    '''
    Used for testing the ML classification model
    '''
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        train_size=train_size,
        random_state= 23
    )
    
    return X_train, X_test, y_train, y_test


def model_fit(model, X_train, X_test, y_train, y_test, X_size, y_size, results, text):
    '''
    Used to analize feature selection methods against a model.
    For the initial process RandomForestClassifier was used
    '''
    model.fit(X_train, y_train)
    r1 = model.score(X_train, y_train)
    r2 = model.score(X_test, y_test)
    results.update({text:[str(X_size),str(y_size),r1,r2]})


def get_remove_columns_target(dataset, remove_columns, target, axis):  
    y = dataset[target]
    X = dataset.drop(remove_columns,axis=axis)

    return X, y


def show_results(r):
    df = pd.DataFrame(
        r,
        index=['size=X_train','size=y_test','train', 'test']
    )
    print(df.head().T)


def classification_flow(id_column, target_column, dataset):
    if id_column:
        remove_columns = [id_column, target_column]
    else:
        remove_columns = [target_column]

    X, y = get_remove_columns_target(
        dataset,
        remove_columns,
        target_column,
        axis=1
    )

    # f_classif: another method
    # X_new = SelectPercentile(score_func=f_classif, percentile=80)

    # mutual_info_classif: another method
    # X_new = SelectPercentile(score_func=mutual_info_classif, percentile=80)

    # Chosen method: chi2
    X_new = SelectPercentile(score_func=chi2, percentile=80)
    fit = X_new.fit(X, y)
    X_new = fit.transform(X)
    score = fit.scores_

    # show column scores
    scores_table = get_feature_scores(score, X.columns, classif=True)

    return scores_table, X_new, fit


def save_to_csv(dataset_new, fit_x):
    '''
    Save autogenerated CSV from the feature selection.

    Output: A Dataframe that later on will be downloaded as CSV
    '''
    features=fit_x.get_feature_names_out()
    return pd.DataFrame(dataset_new,columns=features)
