from django.views.generic import DetailView
from django.shortcuts import render

from .models import Member


class MemberDetail(DetailView):
    model = Member
    context_object_name = 'member'
