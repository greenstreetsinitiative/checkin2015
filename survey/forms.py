from django import forms
from django.forms import ModelForm, HiddenInput

from survey.models import Commutersurvey, Employer, Team, Leg
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from django.forms.util import ErrorList
from django.forms.widgets import HiddenInput

from datetime import datetime


class AlertErrorList(ErrorList):
    """define custom formatting for the leg errors"""
    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return u''
        #FIXME: will this even work as intended?
        for error in self:
            return (u'<div class="alert alert-danger dangerous" '
                    'role="alert">%s</div>' % error)

class CommuterForm(ModelForm):
    class Meta:
        model = Commutersurvey
        fields = ['name', 'email', 'home_address', 'work_address',
                  'employer']
        if not datetime.now().month < 4 or datetime.now().month > 10:
            fields.append('team')

    def __init__(self, *args, **kwargs):
        super(CommuterForm, self).__init__(*args, **kwargs)

        if datetime.now().month < 4 or datetime.now().month > 10:
            # it's not a challenge!
            self.fields['employer'].queryset = Employer.objects.filter(
                nochallenge=True)
            self.fields['employer'].help_text = (
                "Use 'Not employed', 'Self',"
                " or 'Student' as appropriate")
            self.fields['employer'].label = "Employer"
        else:
            # we're in a challenge
            self.fields['employer'].queryset = Employer.objects.filter(
                active2016=True)
            self.fields['team'].queryset = Team.objects.filter(
                parent__active2016=True)
            self.fields['employer'].help_text = (
                "Use 'Not employed', 'Self',"
                " 'Student', or 'Other employer not involved in this year's"
                " Corporate Challenge' as appropriate")
            self.fields['team'].label = "Sub-team"
            self.fields['team'].help_text = (
                "If your company has participating "
                "sub-teams you must choose a sub-team.")

        self.fields['home_address'].help_text = (
            "We do not give your address to other parties. "
            "You may enter an approximate location if you wish.")
        self.fields['work_address'].help_text = (
            "Or, if you are not "
            "employed, other destination")

        # add CSS classes for bootstrap
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['home_address'].widget.attrs['class'] = 'form-control'
        self.fields['work_address'].widget.attrs['class'] = 'form-control'
        self.fields['employer'].widget.attrs['class'] = 'form-control'

        self.fields['home_address'].error_messages['required'] = (
            'Please enter a home address.')
        self.fields['work_address'].error_messages['required'] = (
            'Please enter an address.')
        self.fields['employer'].error_messages['required'] = (
            'Please pick an option from the list.')
        self.fields['email'].error_messages['required'] = (
            'Please enter an email address.')

        if 'team' in self.fields:
            self.fields['team'].widget.attrs['class'] = 'form-control'
            self.fields['team'].required = False

class ExtraCommuterForm(ModelForm):
    class Meta:
        model = Commutersurvey
        fields = ['comments', 'volunteer']

        # TODO: Take into account day and not just month
        if not datetime.now().month < 4 or datetime.now().month > 10:
            fields = ['share'] + fields

    def __init__(self, *args, **kwargs):
        super(ExtraCommuterForm, self).__init__(*args, **kwargs)

        if 'share' in self.fields:
            self.fields['share'].label = (
                "Please don't share my identifying information with my employer")
        self.fields['comments'].label = "Add a comment"
        self.fields['volunteer'].label = (
            "Please contact me with information on ways to help or volunteer"
            " with Green Streets Initiative")
        self.fields['comments'].widget.attrs['placeholder'] = (
            "We'd love to hear from you!")
        self.fields['comments'].widget.attrs['rows'] = 2

        # add CSS classes for bootstrap
        if 'share' in self.fields:
            self.fields['share'].widget.attrs['class'] = 'form-control'
        self.fields['comments'].widget.attrs['class'] = 'form-control'

class RequiredFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
            form.error_class = AlertErrorList

#FIXME: LegForms 1 2 3 and 4 should all be a single class
class LegForm1(ModelForm):

    class Meta:
        model = Leg
        fields = ['mode', 'duration', 'day', 'direction']

    def __init__(self, *args, **kwargs):
        super(LegForm1, self).__init__(*args, **kwargs)

        self.fields['mode'].label = "How you typically travel"
        self.fields['duration'].label = "Time in minutes"

        self.fields['mode'].widget.attrs['class'] = 'form-control'
        self.fields['duration'].widget.attrs['class'] = 'form-control'
        self.fields['day'].initial = 'n'
        self.fields['direction'].initial = 'tw'
        self.fields['day'].widget = HiddenInput()
        self.fields['direction'].widget = HiddenInput()
        self.fields['duration'].error_messages['max_value'] = (
            'Did you really travel a whole day?')
        self.fields['mode'].error_messages['required'] = (
            'Please tell us how you typically travel.')

class LegForm2(ModelForm):

    class Meta:
        model = Leg
        fields = ['mode', 'duration', 'day', 'direction']

    def __init__(self, *args, **kwargs):
        super(LegForm2, self).__init__(*args, **kwargs)

        self.fields['mode'].label = "How you typically travel"
        self.fields['duration'].label = "Time in minutes"

        self.fields['mode'].widget.attrs['class'] = 'form-control'
        self.fields['duration'].widget.attrs['class'] = 'form-control'
        self.fields['day'].initial = 'n'
        self.fields['direction'].initial = 'fw'
        self.fields['day'].widget = HiddenInput()
        self.fields['direction'].widget = HiddenInput()
        self.fields['duration'].error_messages['max_value'] = (
            'Did you really travel a whole day?')
        self.fields['mode'].error_messages['required'] = (
            'Please tell us how you typically travel.')

class LegForm3(ModelForm):

    class Meta:
        model = Leg
        fields = ['mode', 'duration', 'day', 'direction']

    def __init__(self, *args, **kwargs):
        super(LegForm3, self).__init__(*args, **kwargs)

        self.fields['mode'].label = "How you did, or will, travel"
        self.fields['duration'].label = "Time in minutes"

        self.fields['mode'].widget.attrs['class'] = 'form-control'
        self.fields['duration'].widget.attrs['class'] = 'form-control'
        self.fields['day'].initial = 'w'
        self.fields['direction'].initial = 'tw'
        self.fields['day'].widget = HiddenInput()
        self.fields['direction'].widget = HiddenInput()
        self.fields['duration'].error_messages['max_value'] = (
            'Did you really travel a whole day?')
        self.fields['mode'].error_messages['required'] = (
            'Please tell us how you did, or will, travel.')

class LegForm4(ModelForm):

    class Meta:
        model = Leg
        fields = ['mode', 'duration', 'day', 'direction']

    def __init__(self, *args, **kwargs):
        super(LegForm4, self).__init__(*args, **kwargs)

        self.fields['mode'].label = "How you did, or will, travel"
        self.fields['duration'].label = "Time in minutes"

        self.fields['mode'].widget.attrs['class'] = 'form-control'
        self.fields['duration'].widget.attrs['class'] = 'form-control'
        self.fields['day'].initial = 'w'
        self.fields['direction'].initial = 'fw'
        self.fields['day'].widget = HiddenInput()
        self.fields['direction'].widget = HiddenInput()
        self.fields['duration'].error_messages['max_value'] = (
            'Did you really travel a whole day?')
        self.fields['mode'].error_messages['required'] = (
            'Please tell us how you did, or will, travel.')


MakeLegs_WRTW = inlineformset_factory(Commutersurvey, Leg, form=LegForm3, extra=1, max_num=10, can_delete=True)
MakeLegs_WRFW = inlineformset_factory(Commutersurvey, Leg, form=LegForm4,
                                      extra=1, max_num=10, can_delete=True)
MakeLegs_NormalTW = inlineformset_factory(Commutersurvey, Leg, form=LegForm1,
                                          extra=1, max_num=10, can_delete=True)
MakeLegs_NormalFW = inlineformset_factory(Commutersurvey, Leg, form=LegForm2,
                                          extra=1, max_num=10, can_delete=True)
