from django import forms


class FormData(object):

    def __init__(self, field_name, value, form_field):
        self. field_name = field_name
        self.value = value
        self.form_field = form_field


class FormProcessor(object):

    def __init__(self, form_data_list):

        self.form_data_list = form_data_list

    def process(self):

        for form_data in self.form_data_list:
            try:
                self.validate(form_data.value, form_data.form_field)
            except forms.ValidationError as e:
                return {form_data.field_name: e.messages}

        return {}

    def validate(self, data, form_field):

        value = form_field.to_python(data)
        form_field.validate(value)
        form_field.run_validators(value)
