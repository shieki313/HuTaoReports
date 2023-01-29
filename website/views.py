from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from . import forms


class IndexView(FormView):
    form_class = forms.StatusForm
    template_name = "index.html"
    
    def form_valid(self, form):
        data = form.cleaned_data
        testnum = 3
        filenamec = "test.png"
        ctxt = super().get_context_data()
        ctxt["filenamec"] = filenamec
        ctxt["testnum"] = testnum
        return self.render_to_response(ctxt)
    

class AboutView(TemplateView):
    template_name = "about.html"
    
    def get_context_data(self):
        ctxt = super().get_context_data()
        ctxt["skills"] = [
            "Python",
            "C++",
            "Javascript",
            "Rust",
            "Ruby",
            "PHP"
        ]
        ctxt["num_services"] = 1234567
        return ctxt