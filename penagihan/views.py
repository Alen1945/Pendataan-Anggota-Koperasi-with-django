import time
import csv
from django.shortcuts import render,redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import View,ListView,RedirectView
from .models import Penagihan
from .forms import CreatePenagihanForm

# Create your views here.

class ExportData:
	def export_data_csv(self,Data):
		response=HttpResponse(content_type='text/csv')
		response['Content-Disposition']=f"attachment; filename=data-{time.strftime('%y%m%d%H%M%S')}"
		Data=Data.values_list('no_ba','nama_anggota','alamat','no_hp','tanggal','keterangan')
		writer=csv.writer(response)
		writer.writerow(['No BA','Nama Anggota','Alamat','No Hp','Tanggal','Keterangan'])
		for d in Data:
			writer.writerow(d)
		return response


class ListPenagihanView(ListView,ExportData):
	model=Penagihan
	mode=None
	template_name='list_penagihan.html'
	context_object_name='penagihan'
	tahun_sekarang=int(time.strftime('%Y'))+1
	extra_context={
		'title':'Survey/TambahAnggota',
		'daf_tanggal':range(1,32),
		'daf_bulan':range(1,13),
		'daf_tahun':range(2016,tahun_sekarang)
	}
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['penagihan']=self.model.objects.all()
		if 'tahun' in self.request.GET and self.request.GET['tahun']!= 'all':
			tahun=self.request.GET['tahun']
			context['penagihan']=self.model.objects.filter(tanggal__year=tahun)
			if 'bulan' in self.request.GET and self.request.GET['bulan']!= 'all':
				bulan=self.request.GET['bulan']
				context['penagihan']=self.model.objects.filter(tanggal__year=tahun,tanggal__month=bulan)
				if 'tanggal' in self.request.GET and self.request.GET['tanggal']!= 'all':
					tanggal=self.request.GET['tanggal']
					context['penagihan']=self.model.objects.filter(tanggal__year=tahun,tanggal__month=bulan,tanggal__day=tanggal)
		if self.mode=='export':
			context['data']=self.export_data_csv(context['penagihan'])
		return context

	def get(self,request,*args,**kwargs):
		response=super().get(request,*args,**kwargs)
		context=self.get_context_data()
		if self.mode=='export':
			print('alen')
			return context['data']
		return response

	
class CreatePenagihanView(View):
	template_name='tambah_penagihan.html'
	penagihan_form=CreatePenagihanForm()
	mode=None
	context={}
	def get(self,*args,**kwargs):
		if self.mode=='ubah':
			update_data=Penagihan.objects.get(id=kwargs['id_penagihan'])
			data=update_data.__dict__
			self.penagihan_form=CreatePenagihanForm(initial= data,instance=update_data)
			self.context['title']='Ubah Data'
		else:
			self.context['title']='Tambah data'
		self.context['forms']=self.penagihan_form
		return render(self.request,self.template_name,self.context)	

	def post(self,*args,**kwargs):

		if kwargs.__contains__('id_penagihan'):
			update_data=Penagihan.objects.get(id=kwargs['id_penagihan'])
			self.penagihan_form=CreatePenagihanForm(self.request.POST,instance=update_data)
		else:
			  self.penagihan_form=CreatePenagihanForm(self.request.POST)

		if self.penagihan_form.is_valid():
			self.penagihan_form.save()
		return redirect('penagihan:home')

class DeletePenagihanView(RedirectView):
	pattern_name='penagihan:home'
	permanent=False
	query_string=False
	def get_redirect_url(self,*args,**kwargs):
		delete_akun=Penagihan.objects.get(id=kwargs['id_penagihan'])
		delete_akun.delete()
		return super().get_redirect_url()


class SearchView(ListView,ExportData):
	model=Penagihan
	mode=None
	template_name='list_penagihan.html'
	context_object_name='penagihan'
	tahun_sekarang=int(time.strftime('%Y'))+1
	extra_context={
		'title':'Survey/TambahAnggota',
		'daf_tanggal':range(1,32),
		'daf_bulan':range(1,13),
		'daf_tahun':range(2016,tahun_sekarang)
	}
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['penagihan']=self.model.objects.all()
		if 's' in self.request.GET and self.request.GET['s'].strip():
			search=self.request.GET['s']
			context['penagihan']=self.model.objects.filter(Q(no_ba__icontains=search) | Q(nama_anggota__icontains=search) | Q(alamat__icontains=search))
		context['search_export']=1
		if self.mode=='export':
			context['data']=self.export_data_csv(context['penagihan'])
		return context
	def get(self,request,*args,**kwargs):
			response=super().get(request,*args,**kwargs)
			context=self.get_context_data()
			if self.mode=='export':
				return context['data']
			return response