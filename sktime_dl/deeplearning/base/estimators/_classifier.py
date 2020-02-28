# Base class for the Keras neural network classifiers adapted from Fawaz et. al
# https://github.com/hfawaz/dl-4-tsc

__author__ = "James Large, Aaron Bostrom"

import numpy as np

from sktime.classifiers.base import BaseClassifier
from sklearn.utils.validation import check_is_fitted

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

from sktime_dl.utils import save_trained_model, check_and_clean_data


class BaseDeepClassifier(BaseClassifier):

    def __init__(self,
                 model_name=None,
                 model_save_directory=None):
        self.classes_ = None
        self.nb_classes = None
        self.model_save_directory = model_save_directory
        self.model = None
        self.model_name = model_name

    def build_model(self, input_shape, nb_classes, **kwargs):
        """
        Construct a compiled, un-trained, keras model that is ready for training
        ----------
        input_shape : tuple
            The shape of the data fed into the input layer
        nb_classes: int
            The number of classes, which shall become the size of the output layer
        Returns
        -------
        output : a compiled Keras Model
        """
        raise NotImplementedError('this is an abstract method')

    def predict_proba(self, X, input_checks=True, **kwargs):
        """
        Find probability estimates for each class for all cases in X.
        Parameters
        ----------
        X : array-like or sparse matrix of shape = [n_instances, n_columns]
            The training input samples.
            If a Pandas data frame is passed (sktime format)
            If a Pandas data frame is passed, a check is performed that it only has one column.
            If not, an exception is thrown, since this classifier does not yet have
            multivariate capability.
        input_checks: boolean
            whether to check the X parameter
        Returns
        -------
        output : array of shape = [n_instances, n_classes] of probabilities
        """
        check_is_fitted(self)

        X = check_and_clean_data(X, input_checks=input_checks)

        probs = self.model.predict(X, **kwargs)

        # check if binary classification
        if probs.shape[1] == 1:
            # first column is probability of class 0 and second is of class 1
            probs = np.hstack([1 - probs, probs])

        return probs

    # def check_and_clean_data(self, X, y=None, input_checks=True):
    #     if input_checks:
    #         if y is None:
    #             validate_X(X)
    #         else:
    #             validate_X_y(X, y)
    #
    #     # want data in form: [instances = n][timepoints = m][dimensions = d]
    #     if isinstance(X, pd.DataFrame):
    #         if X.shape[1] > 1:
    #             # we have multiple columns
    #             # if cells contain series, this is a multidimensional problem
    #             # else if cells contain single values, this is a univariate problem with values long columns
    #             #      this situation can happen with e.g. forecasting-reduced-to-regression strategies
    #             if isinstance(X.iloc[0, 0], pd.Series):
    #                 # todo investigate incorporating the reshaping into the data extraction instead of this 2-stage process
    #                 X = np.array([[X.iloc[r, c].values for c in range(len(X.columns))] for r in range(len(X))])
    #                 X = X.reshape(X.shape[0], X.shape[2], X.shape[1])  # go from [n][d][m] to [n][m][d]
    #             else:
    #                 X = X.to_numpy()
    #         else:
    #             X = np.asarray([a.values for a in X.iloc[:, 0]])
    #
    #     if len(X.shape) == 2:
    #         # add a dimension to make it multivariate with one dimension
    #         X = X.reshape(X.shape[0], X.shape[1], 1)  # go from [n][m] to [n][m][d=1]
    #
    #     return X

    def save_trained_model(self):
        save_trained_model(
            self.model,
            self.model_save_directory,
            self.model_name)

    def convert_y(self, y):
        self.label_encoder = LabelEncoder()
        self.onehot_encoder = OneHotEncoder(sparse=False, categories='auto')
        # categories='auto' to get rid of FutureWarning

        y = self.label_encoder.fit_transform(y)
        self.classes_ = self.label_encoder.classes_
        self.nb_classes = len(self.classes_)

        y = y.reshape(len(y), 1)
        y = self.onehot_encoder.fit_transform(y)

        return y
