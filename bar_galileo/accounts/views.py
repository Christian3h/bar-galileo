from allauth.account.views import EmailView
from .forms import CustomAddEmailForm

class CustomEmailView(EmailView):
    form_class = CustomAddEmailForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        # Verificamos qué acción se está realizando (qué botón se presionó)
        action = request.POST.get("action")
        
        # Si la acción es agregar un correo, usamos nuestra lógica personalizada
        if action == "add":
            form = self.get_form()
            if form.is_valid():
                # El método save se encarga de la lógica de guardado y envío
                form.save(self.request)
                # El success_url se manejará automáticamente
                return redirect(self.get_success_url())
            else:
                # Si el formulario no es válido, lo volvemos a renderizar con errores
                return self.form_invalid(form)
        
        # Para cualquier otra acción (remove, primary, etc.), usamos la lógica original de allauth
        else:
            return super().post(request, *args, **kwargs)
