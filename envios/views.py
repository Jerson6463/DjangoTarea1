# envios/views.py
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import JsonResponse
from django.views.decorators.http import (
    require_http_methods,
    require_GET,
    require_POST,
)
from django.contrib.auth.decorators import (
    permission_required,
    user_passes_test,
    login_required
)
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from .models import Encomienda, Empleado, HistorialEstado
from .forms import EncomiendaForm
from clientes.models import Cliente
from rutas.models import Ruta
from config.choices import EstadoEnvio
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import CreateView
from django.core.exceptions import PermissionDenied

def mi_vista(request):
    url = reverse('encomienda_detalle', kwargs = {'pk': 1})
    return redirect(url)

class MiView(CreateView):
    succes_url = reverse_lazy('encomienda_lista')

@login_required
def dashboard(request):
    """Vista principal del sistema con estadísticas"""
    hoy = timezone.now().date()
    context = {
        'total_activas': Encomienda.objects.activas().count(),
        'en_transito': Encomienda.objects.en_transito().count(),
        'con_retraso': Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy).count(),
        'ultimas': Encomienda.objects.con_relaciones()[:5],
    }
    return render(request, 'envios/dashboard.html', context)




# request.GET: parámetros de la URLS
@login_required
def encomienda_lista(request):
    qs = Encomienda.objects.con_relaciones()

    estado = request.GET.get('estado', '') # si no existe
    q = request.GET.get('q', '')
    
    qs = Encomienda.objects.con_relaciones()
    
    if estado:
        qs = qs.filter(estado=estado)
        
    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(codigo__icontains=q) |
            Q(remitente__apellidos__icontains=q) |
            Q(destinatario__apellidos__icontains=q)
        )

    paginator = Paginator(qs,15)
    page_number = request.GET.get('page', 1)
    encomiendas = paginator.get_page(page_number)
        
    return render(request, 'envios/lista.html',{
        'encomiendas': encomiendas,
        'estados': EstadoEnvio.choices,
        'estado_activo': estado,
        'q': q,
    })


@login_required
def encomienda_crear(request):
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            enc = form.save()
            messages.success(
                request,
                f'Encomienda {enc.codigo} creada'
            )
            # Redirect envía al usuario a otra página después de una acción exitosa.
            # Evita que el usuario reenvíe el formulario al refrescar la página.
            return redirect('encomienda_detalle',pk=enc.pk)
        else:
            messages.error(request, 'Corriege los errores del formulario.')
    else:
        form = EncomiendaForm()
    
    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': 'Nueva Encomienda',
    })

@login_required
def eliminar_encomienda(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    if enc.estado != 'PE':
        raise PermissionDenied
    
    if request.method == 'POST':
        enc.delete()
        messages.success(request, 'Encomienda eliminada.')
        return redirect('encomienda_lista')
    
    return render (request, 'envios/confirmar_eliminar.html', {'enc':enc})


def encomienda_detalle(request, pk):
    # Busca la encomienda por su ID (primary key). Si no existe, muestra la página 404.
    # Es mucho más seguro que usar .get() que arrojaría un error 500 si falla.
    enc = get_object_or_404(Encomienda, pk=pk)
    
    return render(request, 'envios/detalle.html', {'encomienda': enc})

def encomiendas_por_ruta(request, ruta_pk):
    # Si la búsqueda no arroja resultados y la lista está vacía → devuelve 404
    encomiendas = get_list_or_404(Encomienda, ruta__pk=ruta_pk)
    
    return render(request, 'envios/lista.html', {
        'encomiendas': encomiendas,
    })

def encomienda_editar(request, pk):
    """Editar una encomienda existente."""
    encomienda = get_object_or_404(Encomienda, pk=pk)
    return render(request, 'envios/encomienda_form.html', {
        'encomienda': encomienda
    })


# request.POST: datos del formulario
@require_POST
@login_required
def encomienda_cambiar_estado(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        observacion = request.POST.get('observacion', '')
        
        try:
            empleado = Empleado.objects.get(email=request.user.email)
            enc.cambiar_estado(nuevo_estado, empleado, observacion)
            
            messages.success(request, f'Estado actualizado a: {enc.get_estado_display()}')
        except ValueError as e:
            messages.error(request, str(e))
            
        return redirect('encomienda_detalle', pk=pk)


def buscar_por_codigo(request, codigo):
    """Buscar encomienda por código de seguimiento."""
    encomienda = get_object_or_404(Encomienda, codigo_seguimiento=codigo)
    return render(request, 'envios/encomienda_detalle.html', {
        'encomienda': encomienda
    })
