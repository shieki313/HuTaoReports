from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from . import forms
from django.shortcuts import render
from django.views import View
from .forms import ProcessImageForm
from PIL import Image, ImageOps
from .pyfiles import HuTaoStatus_web
import io
import asyncio


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

class ProcessImageView(View):
    form_class = ProcessImageForm
    template_name = 'process_image.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        image = Image.open('media/img/reportA4.png')
        # buffer = io.BytesIO()
        form = self.form_class(request.POST)
        if form.is_valid():
            a = str(form.cleaned_data['brightness'])
            filepath = 'media/img/file' + a + '.png'
            # image = Image.open(image.image.path)
            # image = ImageOps.adjust_brightness(image, form.cleaned_data['brightness'])
            # image = ImageOps.adjust_contrast(image, form.cleaned_data['contrast'])
            filepath_src = '/' + filepath

            img = asyncio.run(HuTaoStatus_web.main(a))
            img.save(filepath, format=image.format)
            # 815487724　824237286 843715177 813771318
            print(filepath_src)
            return render(request, self.template_name, {'image': filepath_src})
        return render(request, self.template_name, {'form': form})
