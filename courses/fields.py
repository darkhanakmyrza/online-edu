from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)
   
    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
        # Значение пусто.
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # Фильтруем объекты с такими же значениями полей,
                    # перечисленных в "for_fields".
                    query = {field: getattr(model_instance, field)\
                    for field in self.for_fields}
                    qs = qs.filter(**query)
                # Получаем заказ последнего объекта.
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(OrderField, self).pre_save(model_instance, add)

class CourseModuleUpdateView(TemplateResponseMixin, View):
template_name = 'courses/manage/module/formset.html'
course = None
def get_formset(self, data=None):
return ModuleFormSet(instance=self.course,
data=data)
def dispatch(self, request, pk):
self.course = get_object_or_404(Course,
id=pk,
owner=request.user)
return super(CourseModuleUpdateView, self).dispatch(request, pk)
def get(self, request, *args, **kwargs):
formset = self.get_formset()
return self.render_to_response({'course': self.course, 'formset': formset})
def post(self, request, *args, **kwargs):
formset = self.get_formset(data=request.POST)
if formset.is_valid():
formset.save()
return redirect('manage_course_list')
return self.render_to_response({'course': self.course,
'formset': formset})