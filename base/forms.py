from django import forms


class BasePeriodFormset(forms.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        num_open = 0
        times = []

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data['DELETE']:
                continue

            start = form.cleaned_data['start']
            end = form.cleaned_data['end']

            if not end:
                if num_open:
                    raise forms.ValidationError('Du kan bare ha ett åpent intervall om gangen.')
                else:
                    num_open = 1

            for s, e in times:
                if s < start < e or (end and s < end < e):
                    raise forms.ValidationError('Intervaller kan ikke overlappe hverandre.')

            times.append((start, end))
