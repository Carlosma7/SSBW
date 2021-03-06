import logging
import os
import shutil
from .models import Excursion, Fotos, ExcursionSerializer
from .forms import ExcursionForm, RegisterForm
from django.shortcuts import render, redirect
from mongoengine.queryset.visitor import Q
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.signals import user_logged_out
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

IMAGE_DIR = os.path.join(settings.BASE_DIR, 'senderos', 'static', 'img', 'senderos')

def index(request):
	form = ExcursionForm()

	context = {
		'saludo': "buenas tardes",
		'excursiones': Excursion.objects.all()[:4],
		'form': form
	}

	logger.info('Menú principal')

	return render(request, 'senderos/index.html', context)

def buscar(request):
	busqueda = request.POST.get('busqueda','')
	context = {
		'buscado': busqueda,
		'excursiones': Excursion.objects(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda))
	}
	
	logger.info('Barra de búsqueda')

	return render(request, 'senderos/index.html', context)

def editar(request, id):
	if request.method == 'POST':
		form = ExcursionForm(request.POST, request.FILES)

		if form.is_valid():
			e = Excursion.objects.get(id=id)
			input_d = form.cleaned_data
			files 	= request.FILES

			e.nombre = input_d['nombre']
			e.descripcion = input_d['descripcion']
			e.save()

			if len(files) > 0:
				guardarImagenes(id, files, e, input_d)

			messages.success(request, "Ruta editada con éxito")
			logger.info('Ruta editada con éxito')

		else:
			logger.exception('Error al editar la ruta')
			messages.error(request, "Error en el formulario")

	return redirect('index')

def add(request):
	if request.method == 'POST':
		form = ExcursionForm(request.POST, request.FILES)

		if form.is_valid():
			input_d = form.cleaned_data
			files 	= request.FILES
			reg 		= Excursion(nombre = input_d['nombre'], descripcion=input_d['descripcion']).save()

			if len(files) > 0:
				guardarImagenes(str(reg.id), files, reg, input_d)

			messages.success(request, "Ruta añadida con éxito")

			logger.info('Ruta añadida con éxito')

		else:
			logger.exception('Error al añadir la ruta')
			messages.error(request, "Error en el formulario")

	return redirect('index')

def guardarImagenes(id, files, e, input_d):
	directorio = os.path.join(IMAGE_DIR, id)

	try:
		if not os.path.exists(directorio):
			os.mkdir(directorio)

		nombre_archivo = os.path.join(directorio, str(files['foto']))
		with open(nombre_archivo, 'wb+') as dest:
			for chunk in files['foto'].chunks():
				dest.write(chunk)

		if len(e.fotos) == 0:
			e.fotos=[Fotos(pie=input_d.get('pie'), file=input_d.get('foto').name)]
		else:
			e.fotos.append(Fotos(pie=input_d.get('pie'), file=input_d.get('foto').name))

		e.save()
		logger.info('Imagen añadida con éxito')

	except OSError as error:
		logger.exception('Error al añadir foto')
		print('**************** ERROR', error)

def info(request, id):
	form = ExcursionForm()

	context={
		'id_excursion': Excursion.objects(id=id)[0].id,
		'likes': Excursion.objects(id=id)[0].likes,
		'nombre': Excursion.objects(id=id)[0].nombre,
		'descripcion': Excursion.objects(id=id)[0].descripcion,
		'fotos': Excursion.objects(id=id)[0].fotos,
		'n_fotos': len(Excursion.objects(id=id)[0].fotos),
		'comentarios': Excursion.objects(id=id)[0].comentarios,
		'form': form
	}
	
	logger.info('Visualización de la ruta')

	return render(request, 'senderos/info.html', context)

def eliminar(request, id):
	directorio = os.path.join(IMAGE_DIR, id)

	if os.path.exists(directorio):
		shutil.rmtree(directorio)

	Excursion.objects(id=id).delete()
	
	logger.info('Eliminación de la ruta')

	return redirect('index')

def registrar(request):
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
			new_user = authenticate(username=form.cleaned_data['username'],
															password=form.cleaned_data['password1'],
															)
			login(request, new_user)
			logger.info('Usuario registrado')

		else:
			logger.exception('Error al registrar nuevo usuario')

		return redirect("/")

	else:
		logger.exception('Error POST al registrar nuevo usuario')
		form = RegisterForm()

	return render(request, "registration/register.html", {"form":form})

def cambiarMeGusta(request, id):

	if request.is_ajax and request.method == "GET":
		subir = request.GET.dict()["subir"]
		
		e = Excursion.objects.get(id=id)

		likes = e.likes

		if subir == "true":
			e.likes = likes+1

		else:
			e.likes = likes-1

		e.save()

	logger.info('Se han modificado los Me gusta de la ruta')

	return redirect("index")

class ExcursionesView(APIView):

	# permission_classes = (IsAuthenticated,)

	def get(self, request):
		excursiones = Excursion.objects.all()
		serializer = ExcursionSerializer(excursiones, many=True)
		return Response(serializer.data)

	def post(self, request):
		serializer = ExcursionSerializer(data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExcursionView(APIView):

	def get(self, request, id):
		try:
			excursion = Excursion.objects.get(id=id)
			serializer = ExcursionSerializer(excursion)
			return Response(serializer.data)
		except:
			raise Http404

	def delete(self, request, id):
		try:
			e = Excursion.objects.get(id=id)
			e.delete()
			serializer = ExcursionSerializer(e)
			return Response(status=status.HTTP_204_NO_CONTENT)
		except:
			raise Http404

	def put(self, request, id):
		try:
			e = Excursion.objects.get(id=id)
			print("antes del serializer")
			print(request.data.get('nombre'))
			serializer = ExcursionSerializer(e, data=request.data)
			print("despues del serializer")
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		except:
			raise Http404