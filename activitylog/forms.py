# -*- coding: utf-8 -*-

from django import forms


class ActivityLogSearchForm(forms.Form):
    search = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Search log text'}),
        required=False
    )
    search_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'id': "logdatepicker",
                'placeholder': "Search by log date",
                'style': 'text-align: center'
            },
            format='%d-%m-%y',
        ),
        required=False
    )
    hide_empty_jobs = forms.BooleanField(
        widget=forms.CheckboxInput(

        ),
        initial='on',
        required=False
    )
