from django.urls import path
from agrosmartiotweb import views

urlpatterns = [
    path('', views.home, name = "home"),


    


    
    path('gestiondetareas/', views.ProcesoList, name = "gestiondetareas"),
    path('api/', views.ProcesoListAPIView.as_view(),),
    path('exportar_proceso/', views.ExportToExcelViewProceso.as_view(), name='exportar_a_excel_proceso'),
    path('exportar_jornada/', views.ExportToExcelViewJornada.as_view(), name='exportar_a_excel_jornada'),
    path('exportar_trabajador/', views.ExportToExcelViewTrabajador.as_view(), name='exportar_a_excel_trabajador'),






    path('ayuda/', views.ayuda, name = "ayuda"),
 






    path('agregartarea/', views.agregartarea, name = "agregartarea"),
    
    #zona especifica
    path('gestion_zona/', views.gestion_zona, name = "gestion_zona"),
    path('agregarsector/', views.agregar_sector, name = "agregarsector"),
    path('agregar_huerto/<int:sector_id>/', views.agregar_huerto, name='agregar_huerto'),
    path('agregar_huerto_ss/', views.agregar_huerto_sin_sector, name='agregar_huerto_ss'),
    path('agregar_lote_sh/', views.agregar_lote_sin_huerto, name='agregar_lote_sh'),
    path('agregar_lote/', views.agregar_lote, name='agregar_lote'),
    path('modificarsector/<id>', views.modificarsector, name = "modificarsector"),
    path('modificarhuerto/<id>', views.modificarhuerto, name = "modificarhuerto"),
    path('eliminarsector/<int:id>/', views.eliminarsector, name = "eliminarsector"),
    #eliminar huerto
    path('eliminarhuerto/<int:id>/', views.eliminarhuerto, name = "eliminarhuerto"),
    path('modificarlote/<id>', views.modificarlote, name = "modificarlote"),

      

    
    path('modificartarea/<id>', views.modificartarea, name = "modificartarea"),
    path('eliminartarea/<int:id>/', views.eliminartarea, name = "eliminartarea"),
    
    #url trabajadores
    path('gestiondetrabajadores/', views.TrabajadorList, name = "gestiondetrabajadores"),
    path('agregartrabajador/', views.agregartrabajador, name = "agregartrabajador"),
    path('modificartrabajadores/<id>', views.modificartrabajadores, name = "modificartrabajadores"),
    path('eliminarTrabajador/<int:id>/', views.eliminartrabajador, name = "eliminartrabajador"),
    
    path('cargar-lotes/', views.cargar_lotes, name='cargar_lotes'),
    path('agregar_jornada/', views.agregar_jornada, name='agregar_jornada'),
    path('agregar_jornada_por_trato/', views.agregar_jornada_por_trato, name='agregar_jornada_por_trato'),
 
    path('gestion_jornadas/', views.JornadaList, name='gestion_jornadas'),
    path('gestion_jornadas_por_trato/', views.jornada_por_trato_list, name='gestion_jornadas_por_trato'),
    
    
    path('modificarjornada/<id>', views.modificarjornada, name = "modificarjornada"),
    path('eliminarjornada/<int:id>/', views.eliminarjornada, name = "eliminarjornada"),
    path('eliminarjornadaPorTrato/<int:id>/', views.eliminarjornadaPorTrato, name = "eliminarjornadaPorTrato"),

    path('cargar_huertos/', views.cargar_huertos, name='cargar_huertos'),
    path('cargar_lotes/', views.cargar_lotes, name='cargar_lotes'),
  #sensor
    

    path('obtener_cobro/', views.obtener_cobro_view, name='obtener_cobro'),





    
    #registration
    path('obtener_cobro/', views.obtener_cobro_view, name='obtener_cobro'),

    #registration
    path('register/', views.register, name='register'),
    path('register_colaborador/', views.register_colaborador, name='register_colaborador'),
    
    path('accounts/login/', views.my_login, name='my_login'), 
    path('user_logout/', views.user_logout, name='user_logout'),
    path('list_all_users/', views.list_all_users, name='list_all_users'),
    path('list_colaboradores/', views.list_colaboradores, name='list_colaboradores'),

    #deleteuser
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    #empresa
    path('agregar_empresa/', views.agregar_empresa, name='agregar_empresa'),  # Para agregar una empresa o fundo

    # Colaborador URLs
    path('lista_empresas/', views.lista_empresas, name='lista_empresas'),

    #edita colaborador 
    path('edit_colaborador/<int:user_id>/', views.edit_colaborador_view, name='edit_colaborador'),

    path('crear_sectorPoligon/', views.crear_sectorPoligon, name='crear_sectorPoligon'),
    path('gestion_zonaPoligon/', views.gestion_zonaPoligon, name='gestion_zonaPoligon'),

  

   
    path('gestion_finanzas/', views.gestion_finanzas, name='gestion_finanzas'),


    path('receive-data/', views.receive_data, name='receive_data'),
    path('receive-data-soil/', views.receive_data_soil, name='receive_data_soil'),

    path('tiemporealsoil/', views.combined_data_view_soil, name='tiemporealsoil'),
    
    path('tiemporeal/', views.combined_data_view, name='tiemporeal'),
    path('informes/', views.informes, name = "informes"),


    path('cuadernodecampo/', views.cuadernodecampo, name='cuadernodecampo'),

    path('cosechas_list/', views.cosechas_list, name='cosechas_list'),  # Lista de cosechas
    path('crear_cosecha', views.crear_cosecha, name='crear_cosecha'),  # Crear nueva cosecha




]

