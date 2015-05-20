from django import forms
from django.forms import ModelForm, HiddenInput

from survey.models import Commutersurvey, Employer, Team, Leg
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from django.forms.util import ErrorList
from django.forms.widgets import HiddenInput

# define custom formatting for the leg errors
class AlertErrorList(ErrorList):
  def __unicode__(self):
    return self.as_divs()

  def as_divs(self):
    if not self: return u''
    for e in self:
      return u'<div class="alert alert-danger dangerous" role="alert">%s</div>' % e

class CommuterForm(ModelForm):
  class Meta:
      model = Commutersurvey
      fields = ['name', 'email', 'home_address', 'work_address']

  # provides a dropdown list of active employers
  employer = forms.ModelChoiceField(queryset=Employer.objects.filter(active2015=True))

  # provides a dropdown list of teams
  team = forms.ModelChoiceField(queryset=Team.objects.filter(parent__active2015=True))

  def __init__(self, *args, **kwargs):
      super(CommuterForm, self).__init__(*args, **kwargs)

      self.fields['employer'].label = "Employer (use 'None/Self', 'Student', or 'Other employer not involved in this year’s Corporate Challenge' as appropriate)"
      self.fields['team'].label = "Sub-team (if applicable)"
      self.fields['work_address'].label = "Workplace Address (or, if you are not employed, other destination)"

      # add CSS classes for bootstrap
      self.fields['name'].widget.attrs['class'] = 'form-control'
      self.fields['email'].widget.attrs['class'] = 'form-control'
      self.fields['home_address'].widget.attrs['class'] = 'form-control'
      self.fields['work_address'].widget.attrs['class'] = 'form-control'
      self.fields['employer'].widget.attrs['class'] = 'form-control'
      self.fields['team'].widget.attrs['class'] = 'form-control'
      self.fields['team'].required = False
      self.fields['home_address'].error_messages['required'] = 'Please enter a home address.'
      self.fields['work_address'].error_messages['required'] = 'Please enter an address.'
      self.fields['employer'].error_messages['required'] = 'Please pick an option from the list.'
      self.fields['email'].error_messages['required'] = 'Please enter an email address.'

class ExtraCommuterForm(ModelForm):
  class Meta:
      model = Commutersurvey
      fields = ['share', 'comments']

  def __init__(self, *args, **kwargs):
      super(ExtraCommuterForm, self).__init__(*args, **kwargs)

      self.fields['share'].label = "Please don't share my identifying information with my employer"
      self.fields['comments'].label = "Add a comment"
      self.fields['comments'].widget.attrs['placeholder'] = "We'd love to hear from you!"
      self.fields['comments'].widget.attrs['rows'] = 2

      # add CSS classes for bootstrap
      self.fields['share'].widget.attrs['class'] = 'form-control'
      self.fields['comments'].widget.attrs['class'] = 'form-control'

class RequiredFormSet(BaseInlineFormSet):

  def __init__(self, *args, **kwargs):
      super(RequiredFormSet, self).__init__(*args, **kwargs)
      for form in self.forms:
          form.empty_permitted = False
          form.error_class = AlertErrorList

class LegForm1(ModelForm):

  class Meta:
    model = Leg
    fields = ['mode', 'duration', 'day', 'direction']

  def __init__(self, *args, **kwargs):
    super(LegForm1, self).__init__(*args, **kwargs)

    self.fields['mode'].label = "How you traveled"
    self.fields['duration'].label = "Time in minutes"

    self.fields['mode'].widget.attrs['class'] = 'form-control'
    self.fields['duration'].widget.attrs['class'] = 'form-control'
    self.fields['day'].initial = 'n'
    self.fields['direction'].initial = 'tw'
    self.fields['day'].widget = HiddenInput()
    self.fields['direction'].widget = HiddenInput()
    self.fields['duration'].error_messages['max_value'] = 'Did you really travel a whole day?'
    self.fields['mode'].error_messages['required'] = 'Please tell us how you traveled.'
    self.fields['mode'].required = False
    self.fields['duration'].required = False

class LegForm2(ModelForm):

  class Meta:
    model = Leg
    fields = ['mode', 'duration', 'day', 'direction']

  def __init__(self, *args, **kwargs):
    super(LegForm2, self).__init__(*args, **kwargs)

    self.fields['mode'].label = "How you traveled"
    self.fields['duration'].label = "Time in minutes"

    self.fields['mode'].widget.attrs['class'] = 'form-control'
    self.fields['duration'].widget.attrs['class'] = 'form-control'
    self.fields['day'].initial = 'n'
    self.fields['direction'].initial = 'fw'
    self.fields['day'].widget = HiddenInput()
    self.fields['direction'].widget = HiddenInput()
    self.fields['duration'].error_messages['max_value'] = 'Did you really travel a whole day?'
    self.fields['mode'].error_messages['required'] = 'Please tell us how you traveled.'
    self.fields['mode'].required = False
    self.fields['duration'].required = False

class LegForm3(ModelForm):

  class Meta:
    model = Leg
    fields = ['mode', 'duration', 'day', 'direction']

  def __init__(self, *args, **kwargs):
    super(LegForm3, self).__init__(*args, **kwargs)

    self.fields['mode'].label = "How you traveled"
    self.fields['duration'].label = "Time in minutes"

    self.fields['mode'].widget.attrs['class'] = 'form-control'
    self.fields['duration'].widget.attrs['class'] = 'form-control'
    self.fields['day'].initial = 'w'
    self.fields['direction'].initial = 'tw'
    self.fields['day'].widget = HiddenInput()
    self.fields['direction'].widget = HiddenInput()
    self.fields['duration'].error_messages['max_value'] = 'Did you really travel a whole day?'
    self.fields['mode'].error_messages['required'] = 'Please tell us how you traveled.'

class LegForm4(ModelForm):

  class Meta:
    model = Leg
    fields = ['mode', 'duration', 'day', 'direction']

  def __init__(self, *args, **kwargs):
    super(LegForm4, self).__init__(*args, **kwargs)

    self.fields['mode'].label = "How you traveled"
    self.fields['duration'].label = "Time in minutes"

    self.fields['mode'].widget.attrs['class'] = 'form-control'
    self.fields['duration'].widget.attrs['class'] = 'form-control'
    self.fields['day'].initial = 'w'
    self.fields['direction'].initial = 'fw'
    self.fields['day'].widget = HiddenInput()
    self.fields['direction'].widget = HiddenInput()
    self.fields['duration'].error_messages['max_value'] = 'Did you really travel a whole day?'
    self.fields['mode'].error_messages['required'] = 'Please tell us how you traveled.'
    self.fields['mode'].required = False
    self.fields['duration'].required = False


MakeLegs_WRTW = inlineformset_factory(Commutersurvey, Leg, form=LegForm3, extra=1, max_num=10, can_delete=True)
# MakeLegs_WRTW = inlineformset_factory(Commutersurvey, Leg, formset=RequiredFormSet, form=LegForm3, extra=1, max_num=10, can_delete=True)
MakeLegs_WRFW = inlineformset_factory(Commutersurvey, Leg, form=LegForm4, extra=1, max_num=10, can_delete=True)
MakeLegs_NormalTW = inlineformset_factory(Commutersurvey, Leg, form=LegForm1, extra=1, max_num=10, can_delete=True)
MakeLegs_NormalFW = inlineformset_factory(Commutersurvey, Leg, form=LegForm2, extra=1, max_num=10, can_delete=True)

class NormalFromWorkSameAsAboveForm(forms.Form):
  normal_same_as_reverse = forms.BooleanField(widget=forms.RadioSelect(choices=((True,'YES'),(False,'NO'))), initial=True, label='I did the same as to work, but in reverse.')

class WalkRideFromWorkSameAsAboveForm(forms.Form):
  walkride_same_as_reverse = forms.BooleanField(widget=forms.RadioSelect(choices=((True,'YES'),(False,'NO'))), initial=True, label='I did the same as to work, but in reverse.')

class NormalIdenticalToWalkrideForm(forms.Form):
  normal_same_as_walkride = forms.BooleanField(widget=forms.RadioSelect(choices=((True,'YES'),(False,'NO'))), initial=True, label='My normal commute is exactly like my walk ride day commute.')
