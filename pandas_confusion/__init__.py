#!/usr/bin/python
# -*- coding: utf8 -*-

"""
Confusion matrix
"""

import math
import numpy as np
import pandas as pd
from enum import Enum  # pip install enum34
import matplotlib.pylab as plt


class Backend(Enum):
    Matplotlib = 1
    Seaborn = 2


BACKEND_DEFAULT = Backend.Matplotlib
SUM_LABEL_DEFAULT = '__all__'
DISPLAY_SUM_DEFAULT = True

class ConfusionMatrix(object):
    """Confusion matrix"""
    
    def __init__(self, y_actu, y_pred, display_sum=DISPLAY_SUM_DEFAULT, backend=BACKEND_DEFAULT):

        if isinstance(y_actu, pd.Series):
            self.y_actu = y_actu
        else:
            self.y_actu = pd.Series(y_actu)
            
        if isinstance(y_pred, pd.Series):
            self.y_pred = y_pred
        else:
            self.y_pred = pd.Series(y_pred)
        
        self._df_confusion = pd.crosstab(self.y_actu, self.y_pred, rownames=['Actual'], colnames=['Predicted'])
        #self._df_confusion.index.name = 'Actual'
        #self._df_confusion.columns.name = 'Predicted'

        self._df_conf_norm = self._df_confusion / self._df_confusion.sum(axis=1)

        self.backend = backend
        self.display_sum = display_sum

    def __repr__(self):
        return(self.dataframe(sum=self.display_sum).__repr__())

    def __str__(self):
        return(self.dataframe(sum=self.display_sum).__str__())

    def dataframe(self, normalized=False, sum=False, sum_label=SUM_LABEL_DEFAULT):
        if normalized:
            df = self._df_conf_norm
        else:
            df = self._df_confusion

        if sum:
            df = df.copy()
            df[sum_label] = df.sum(axis=1)
            #df = pd.concat([df, pd.DataFrame(df.sum(axis=1), columns=[sum_label])], axis=1)
            df = pd.concat([df, pd.DataFrame(df.sum(axis=0), columns=[sum_label]).T])
        
        return(df)

    def array(self, normalized=False, sum=False, sum_label=SUM_LABEL_DEFAULT):
        return(self.dataframe(normalized, sum, sum_label).values)

    def plot(self, normalized=False, backend=None, **kwargs):
        """
        plot confusion matrix
        """

        if normalized:
            df = self._df_conf_norm
        else:
            df = self._df_confusion

        if 'cmap' not in kwargs.keys():
            cmap = plt.cm.gray_r

        if backend is None:
            backend = self.backend

        if backend == Backend.Matplotlib:
            plt.matshow(df, cmap=cmap) # imshow
            #plt.title(title)
            plt.colorbar()
            tick_marks = np.arange(len(df.columns))
            plt.xticks(tick_marks, df.columns, rotation=45)
            plt.yticks(tick_marks, df.index)
            #plt.tight_layout()
            plt.ylabel(df.index.name)
            plt.xlabel(df.columns.name)


        elif backend == Backend.Seaborn:
            import seaborn as sns
            sns.heatmap(df, **kwargs)
            # You should test this yourself
            # because I'm facing an issue with Seaborn under Mac OS X (2015-04-26)
            # RuntimeError: Cannot get window extent w/o renderer

        else:
            raise(NotImplementedError)


class BinaryConfusionMatrix(ConfusionMatrix):
    """Binary confusion matrix"""
    
    def __init__(self, y_actu, y_pred):
        super(BinaryConfusionMatrix, self).__init__(y_actu, y_pred)

    @property
    def P(self):
        """Positive"""
        return(self._df_confusion.loc[True, :].sum())
    
    @property
    def N(self):
        """Negative"""
        return(self._df_confusion.loc[False, :].sum())
    
    @property
    def TP(self):
        """
        true positive (TP)
        eqv. with hit
        """
        return(self._df_confusion.loc[True, True])
    
    @property
    def TN(self):
        """
        true negative (TN)
        eqv. with correct rejection
        """
        return(self._df_confusion.loc[False, False])
    
    @property
    def FN(self):
        """
        false negative (FN)
        eqv. with miss, Type II error
        """
        return(self._df_confusion.loc[True, False])
    
    @property
    def FP(self):
        """
        false positive (FP)
        eqv. with false alarm, Type I error
        """
        return(self._df_confusion.loc[False, True])
    
    @property
    def FPR(self):
        """
        fall-out or false positive rate (FPR)
        \mathit{FPR} = \mathit{FP} / N = \mathit{FP} / (\mathit{FP} + \mathit{TN})
        """
        #return(float(self.FP)/(self.FP + self.TN))
        return(float(self.FP) / self.N)
    
    @property
    def TPR(self):
        """
        sensitivity or true positive rate (TPR)
        eqv. with hit rate, recall
        \mathit{TPR} = \mathit{TP} / P = \mathit{TP} / (\mathit{TP}+\mathit{FN})
        """
        #return(float(self.TP) / (self.TP + self.FN))
        return(float(self.TP) / self.P)

    @property
    def sensitivity(self):
        """
        same as TPR
        """
        return(self.TPR)


    @property
    def TNR(self):
        """
        specificity (SPC) or true negative rate (TNR)
        \mathit{SPC} = \mathit{TN} / N = \mathit{TN} / (\mathit{FP} + \mathit{TN}) 
        """
        return(float(self.TN) / self.N)

    @property
    def SPC(self):
        """
        same as TNR
        """
        return(self.TNR)

    @property
    def specificity(self):
        """
        same as TNR
        """
        return(self.TNR)

    @property
    def PPV(self):
        """
        precision or positive predictive value (PPV)
        \mathit{PPV} = \mathit{TP} / (\mathit{TP} + \mathit{FP})
        """
        return(float(self.TP) / (self.TP + self.FP))

    @property
    def precision(self):
        """
        same as PPV
        """
        return(self.PPV)

    @property
    def NPV(self):
        """
        negative predictive value (NPV)
        \mathit{NPV} = \mathit{TN} / (\mathit{TN} + \mathit{FN})
        """
        return(float(self.TN) / (self.TN + self.FN))
    
    @property
    def FDR(self):
        """
        false discovery rate (FDR)
        \mathit{FDR} = \mathit{FP} / (\mathit{FP} + \mathit{TP}) = 1 - \mathit{PPV} 
        """
        return(1 - self.PPV)
    
    @property
    def FNR(self):
        """
        Miss Rate or False Negative Rate (FNR)
        \mathit{FNR} = \mathit{FN} / P = \mathit{FN} / (\mathit{FN} + \mathit{TP}) 
        """
        return(float(self.FN) / self.P)
    
    @property
    def ACC(self):
        """
        accuracy (ACC)
        \mathit{ACC} = (\mathit{TP} + \mathit{TN}) / (P + N)
        """
        return(float(self.TP + self.TN) / (self.P + self.N))
    
    @property
    def F1_score(self):
        """
        F1 score is the harmonic mean of precision and sensitivity
        \mathit{F1} = 2 \mathit{TP} / (2 \mathit{TP} + \mathit{FP} + \mathit{FN})
        """
        return(2 * float(self.TP)/(2 * self.TP + self.FP + self.FN))
    
    @property
    def MCC(self):
        """
        Matthews correlation coefficient (MCC)
        \frac{ TP \times TN - FP \times FN } {\sqrt{ (TP+FP) ( TP + FN ) ( TN + FP ) ( TN + FN ) } }
        """
        return((self.TP * self.TN - self.FP * self.FN) \
            / math.sqrt((self.TP + self.FP) * ( self.TP + self.FN ) *\
            ( self.TN + self.FP ) * ( self.TN + self.FN )))
    
    @property
    def informedness(self):
        """
        Informedness = Sensitivity + Specificity - 1
        """
        return(self.sensitivity + self.specificity - 1.0)
    
    @property
    def markedness(self):
        """
        Markedness = Precision + NPV - 1
        """
        return(self.precision + self.NPV - 1.0)
