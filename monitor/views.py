from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.db.models import Q, Count
from .models import RegistrationInfo, Asset, School
from django.core.paginator import Paginator
import os
import json
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Use this for month logic
from datetime import date
import io
from django.db.models import Count
from django.http import HttpResponse


def download_pdf_device(request):
    queryset = request.session.get('timing_logs', [])

    if not queryset:
        return HttpResponse("No data available to generate PDF.", status=204)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Device Timing Report")
    y -= 40

    p.setFont("Helvetica", 10)

    for i, log in enumerate(queryset, start=1):
        if y < 150:  # Avoid printing at the bottom margin
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 50

        # Write details line by line
        p.drawString(50, y, f"Sr No       : {i}")
        y -= 15
        p.drawString(50, y, f"Dise Code   : {log.get('dise_code', '')}")
        y -= 15
        p.drawString(50, y, f"School      : {log.get('school', '')}")
        y -= 15
        p.drawString(50, y, f"Serial No.  : {log.get('serial_number', '')}")
        y -= 15
        p.drawString(50, y, f"Date        : {log.get('date', '')}")
        y -= 15
        p.drawString(50, y, f"Start Time  : {log.get('start_time', '')}")
        y -= 15
        p.drawString(50, y, f"End Time    : {log.get('end_time', '')}")
        y -= 15
        p.drawString(50, y, f"Duration    : {log.get('duration', '')}")
        y -= 30  # Extra space between entries

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="timing_report_device.pdf"'
    return response

def download_pdf_activity(request):
    queryset = request.session.get('timing_logs', [])

    if not queryset:
        return HttpResponse("No data available to generate PDF.", status=204)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Application Timing Report")
    y -= 40

    p.setFont("Helvetica", 10)

    for i, log in enumerate(queryset, start=1):
        if y < 150:  # Avoid printing at the bottom margin
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 50

        # Write details line by line
        p.drawString(50, y, f"Sr No       : {i}")
        y -= 15
        p.drawString(50, y, f"Dise Code   : {log.get('dise_code', '')}")
        y -= 15
        p.drawString(50, y, f"School      : {log.get('school', '')}")
        y -= 15
        p.drawString(50, y, f"Application  : {log.get('package_name', '')}")
        y -= 15
        p.drawString(50, y, f"Serial No.  : {log.get('serial_number', '')}")
        y -= 15
        p.drawString(50, y, f"Date        : {log.get('date', '')}")
        y -= 15
        p.drawString(50, y, f"Start Time  : {log.get('start_time', '')}")
        y -= 15
        p.drawString(50, y, f"End Time    : {log.get('end_time', '')}")
        y -= 15
        p.drawString(50, y, f"Duration    : {log.get('duration', '')}")
        y -= 30  # Extra space between entries

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="timing_report_activity.pdf"'
    return response

def reportActivitytime(request):
    queryset = []
    timing_logs = []

    # Get POST selections
    dise_code = request.POST.get('dise', '').strip()
    selected_district = ''
    selected_block = ''
    selected_village = ''
    selected_school = ''
    selected_serial = request.POST.get('serial_number', '').strip()
    fdate= request.POST.get('fdate', '').strip()
    tdate=''
    timeperiod=request.POST.get('timeperiod', '').strip()
    districts = School.objects.values_list('district', flat=True).distinct().order_by('district')
    blocks, villages, schools = [], [], []
    
    # Fetch related location fields if dise code is given
    if dise_code:
        try:
            school_obj = School.objects.get(dise_code=dise_code)
            selected_district = school_obj.district
            selected_block = school_obj.block
            selected_village = school_obj.village
            selected_school = school_obj.school_name

            blocks = School.objects.filter(district=selected_district).values_list('block', flat=True).distinct().order_by('block')
            villages = School.objects.filter(block=selected_block).values_list('village', flat=True).distinct().order_by('village')
            schools = School.objects.filter(village=selected_village).values_list('school_name', flat=True).distinct().order_by('school_name')
        except School.DoesNotExist:
            pass
    if fdate:
        try:
            fdate_obj = datetime.strptime(fdate, "%Y-%m-%d").date()
            if timeperiod == "Weekly":
                tdate = fdate_obj + timedelta(days=6)
            elif timeperiod == "Monthly":
                tdate = fdate_obj + relativedelta(months=1) - timedelta(days=1)
            elif timeperiod == "Quarterly":
                tdate = fdate_obj + relativedelta(months=3) - timedelta(days=1)
            else:
                tdate = fdate_obj
        except ValueError:
            tdate = ''

    # Convert tdate to string before passing to template
    if tdate:
        tdate = tdate.strftime("%Y-%m-%d")
    # Serial numbers relat
    # ed to dise code
    serials = Asset.objects.filter(dise__dise_code=dise_code).values_list('serial_number', flat=True).distinct().order_by('serial_number') if dise_code else []

    # Generate button logic
    if request.method == "POST" and 'generate' in request.POST:
        queryset = Asset.objects.select_related('dise').all()

        if dise_code:
            queryset = queryset.filter(dise__dise_code__icontains=dise_code)
        if selected_serial:
            queryset = queryset.filter(serial_number__icontains=selected_serial)
        if fdate and tdate:
            queryset = queryset.filter(date__range=[fdate, tdate])

        for asset in queryset:
            json_path = os.path.join(settings.BASE_DIR, 'media', 'data', f'{asset.serial_number}_app_data.json')
            if os.path.exists(json_path):
                with open(json_path) as f:
                    json_data = json.load(f)
                    if isinstance(json_data, list):
                        entries = json_data
                    for entry in entries:    
                        timing_logs.append({
                            'serial_number': asset.serial_number,
                            'dise_code': dise_code,
                            'package_name': entry.get('package_name'),
                            'date': entry.get('date'),
                            'start_time': entry.get('start_time'),
                            'end_time': entry.get('end_time'),
                            'duration': entry.get('duration'),
                            'school': asset.dise.school_name,
                            'block': asset.dise.block,
                        })
    request.session['timing_logs'] = timing_logs

    return render(request, 'monitor/reportActivitytime.html', {
        'queryset': queryset,
        'districts': districts,
        'blocks': blocks,
        'villages': villages,
        'schools': schools,
        'serials': serials,
        'selected_district': selected_district,
        'selected_block': selected_block,
        'selected_village': selected_village,
        'selected_school': selected_school,
        'selected_serial': selected_serial,
        'fdate': fdate,
        'tdate': tdate,
        'timing_logs': timing_logs,
        'timeperiod': timeperiod,
        'dise_code': dise_code,
    })

def schoolLogs(request):
    queryset = []
    timing_logs = []
    count=0

    # Get POST selections
    dise_code = request.POST.get('dise', '').strip()
    selected_district = ''
    selected_block = ''
    selected_village = ''
    selected_school = ''
    selected_serial = request.POST.get('serial_number', '').strip()
    fdate= request.POST.get('fdate', '').strip()
    tdate=''
    timeperiod=request.POST.get('timeperiod', '').strip()
    districts = School.objects.values_list('district', flat=True).distinct().order_by('district')
    blocks, villages, schools = [], [], []
    
    # Fetch related location fields if dise code is given
    if dise_code:
        try:
            school_obj = School.objects.get(dise_code=dise_code)
            selected_district = school_obj.district
            selected_block = school_obj.block
            selected_village = school_obj.village
            selected_school = school_obj.school_name

            blocks = School.objects.filter(district=selected_district).values_list('block', flat=True).distinct().order_by('block')
            villages = School.objects.filter(block=selected_block).values_list('village', flat=True).distinct().order_by('village')
            schools = School.objects.filter(village=selected_village).values_list('school_name', flat=True).distinct().order_by('school_name')
        except School.DoesNotExist:
            pass
    if fdate:
        try:
            fdate_obj = datetime.strptime(fdate, "%Y-%m-%d").date()
            if timeperiod == "Weekly":
                tdate = fdate_obj + timedelta(days=6)
            elif timeperiod == "Monthly":
                tdate = fdate_obj + relativedelta(months=1) - timedelta(days=1)
            elif timeperiod == "Quarterly":
                tdate = fdate_obj + relativedelta(months=3) - timedelta(days=1)
            else:
                tdate = fdate_obj
        except ValueError:
            tdate = ''

    # Convert tdate to string before passing to template
    if tdate:
        tdate = tdate.strftime("%Y-%m-%d")
    # Serial numbers relat
    # ed to dise code
    serials = Asset.objects.filter(dise__dise_code=dise_code).values_list('serial_number', flat=True).distinct().order_by('serial_number') if dise_code else []
    if request.method == "POST" and 'device' in request.POST:
        queryset = Asset.objects.select_related('dise').all()

        if dise_code:
            queryset = queryset.filter(dise__dise_code__icontains=dise_code)
        if selected_serial:
            queryset = queryset.filter(serial_number__icontains=selected_serial)
        if fdate and tdate:
            queryset = queryset.filter(date__range=[fdate, tdate])

        for asset in queryset:
            json_path = os.path.join(settings.BASE_DIR, 'media', 'data', f'{asset.serial_number}_timing_data.json')
            if os.path.exists(json_path):
                with open(json_path) as f:
                    json_data = json.load(f)
                    for entry in json_data.get('entries', []):
                        timing_logs.append({
                            'serial_number': asset.serial_number,
                            'dise_code': dise_code,
                            'date': entry.get('date'),
                            'start_time': entry.get('start_time'),
                            'end_time': entry.get('end_time'),
                            'duration': entry.get('duration'),
                            'school': asset.dise.school_name,
                            'block': asset.dise.block,
                            'count':count
                        })
    request.session['timing_logs'] = timing_logs

    # Generate button logic
    if request.method == "POST" and 'application' in request.POST:
        count=1
        queryset = Asset.objects.select_related('dise').all()

        if dise_code:
            queryset = queryset.filter(dise__dise_code__icontains=dise_code)
        if selected_serial:
            queryset = queryset.filter(serial_number__icontains=selected_serial)
        if fdate and tdate:
            queryset = queryset.filter(date__range=[fdate, tdate])

        for asset in queryset:
            json_path = os.path.join(settings.BASE_DIR, 'media', 'data', f'{asset.serial_number}_app_data.json')
            if os.path.exists(json_path):
                with open(json_path) as f:
                    json_data = json.load(f)
                    if isinstance(json_data, list):
                        entries = json_data
                    for entry in entries:    
                        timing_logs.append({
                            'serial_number': asset.serial_number,
                            'dise_code': dise_code,
                            'package_name': entry.get('package_name'),
                            'date': entry.get('date'),
                            'start_time': entry.get('start_time'),
                            'end_time': entry.get('end_time'),
                            'duration': entry.get('duration'),
                            'school': asset.dise.school_name,
                            'block': asset.dise.block,
                            'count':count
                        })
    request.session['timing_logs'] = timing_logs

    return render(request, 'monitor/schoolLogs.html', {
        'queryset': queryset,
        'districts': districts,
        'blocks': blocks,
        'villages': villages,
        'schools': schools,
        'serials': serials,
        'selected_district': selected_district,
        'selected_block': selected_block,
        'selected_village': selected_village,
        'selected_school': selected_school,
        'selected_serial': selected_serial,
        'fdate': fdate,
        'tdate': tdate,
        'timing_logs': timing_logs,
        'timeperiod': timeperiod,
        'dise_code': dise_code,
        'count':count,
    })
    
def download_csv_device(request):
    queryset = request.session.get('timing_logs', [])

    if not queryset:
        return HttpResponse("No data available to download.", status=204)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timing_report_device.csv"'

    writer = csv.writer(response)
    writer.writerow(['Sr','Dise Code','School', 'Serial Number', 'Date', 'Start Time', 'End Time', 'Duration'])

    for i, log in enumerate(queryset, start=1):
        writer.writerow([
            i,
            log.get('dise_code', ''),
            log.get('school', ''),
            log.get('serial_number', ''),
            log.get('date', ''),
            log.get('start_time', ''),
            log.get('end_time', ''),
            log.get('duration', '')
        ])

    return response


def download_csv_activity(request):
    queryset = request.session.get('timing_logs', [])

    if not queryset:
        return HttpResponse("No data available to download.", status=204)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timing_report_activity.csv"'

    writer = csv.writer(response)
    writer.writerow(['Sr','Dise Code','School','Package Name', 'Serial Number', 'Date', 'Start Time', 'End Time', 'Duration'])

    for i, log in enumerate(queryset, start=1):
        writer.writerow([
            i,
            log.get('dise_code', ''),
            log.get('school', ''),
            log.get('package_name', ''),
            log.get('serial_number', ''),
            log.get('date', ''),
            log.get('start_time', ''),
            log.get('end_time', ''),
            log.get('duration', '')
        ])

    return response


def download_csv_asset(request):
    queryset = request.session.get('timing_logs', [])

    if not queryset:
        return HttpResponse("No data available to download.", status=204)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timing_report_asset.csv"'

    writer = csv.writer(response)
    writer.writerow(['Sr','Dise Code','School','District','Block','Lab','Computer No.','Desktop Serial','TFT Serial','Webcam Serial','Headphone Serial','Switch Serial', 'Reg. Date'])

    for i, log in enumerate(queryset, start=1):
        writer.writerow([
            i,
            log.get('dise_code', ''),
            log.get('school', ''),
            log.get('district', ''),
            log.get('block', ''),
            log.get('lab', ''),
            log.get('pc', ''),
            log.get('serial_number', ''),
            log.get('tft', ''),
            log.get('webcam', ''),
            log.get('headphone', ''),
            log.get('switch', ''),
            log.get('date', '')
        ])

    return response

def reportDevicetime(request):
    queryset = []
    timing_logs = []

    # Get POST selections
    dise_code = request.POST.get('dise', '').strip()
    selected_district = ''
    selected_block = ''
    selected_village = ''
    selected_school = ''
    selected_serial = request.POST.get('serial_number', '').strip()
    fdate= request.POST.get('fdate', '').strip()
    tdate=''
    timeperiod=request.POST.get('timeperiod', '').strip()
    districts = School.objects.values_list('district', flat=True).distinct().order_by('district')
    blocks, villages, schools = [], [], []
    
    # Fetch related location fields if dise code is given
    if dise_code:
        try:
            school_obj = School.objects.get(dise_code=dise_code)
            selected_district = school_obj.district
            selected_block = school_obj.block
            selected_village = school_obj.village
            selected_school = school_obj.school_name

            blocks = School.objects.filter(district=selected_district).values_list('block', flat=True).distinct().order_by('block')
            villages = School.objects.filter(block=selected_block).values_list('village', flat=True).distinct().order_by('village')
            schools = School.objects.filter(village=selected_village).values_list('school_name', flat=True).distinct().order_by('school_name')
        except School.DoesNotExist:
            pass
    if fdate:
        try:
            fdate_obj = datetime.strptime(fdate, "%Y-%m-%d").date()
            if timeperiod == "Weekly":
                tdate = fdate_obj + timedelta(days=6)
            elif timeperiod == "Monthly":
                tdate = fdate_obj + relativedelta(months=1) - timedelta(days=1)
            elif timeperiod == "Quarterly":
                tdate = fdate_obj + relativedelta(months=3) - timedelta(days=1)
            else:
                tdate = fdate_obj
        except ValueError:
            tdate = ''

    # Convert tdate to string before passing to template
    if tdate:
        tdate = tdate.strftime("%Y-%m-%d")
    # Serial numbers related to dise code
    serials = Asset.objects.filter(dise__dise_code=dise_code).values_list('serial_number', flat=True).distinct().order_by('serial_number') if dise_code else []

    # Generate button logic
    if request.method == "POST" and 'generate' in request.POST:
        queryset = Asset.objects.select_related('dise').all()

        if dise_code:
            queryset = queryset.filter(dise__dise_code__icontains=dise_code)
        if selected_serial:
            queryset = queryset.filter(serial_number__icontains=selected_serial)
        if fdate and tdate:
            queryset = queryset.filter(date__range=[fdate, tdate])

        for asset in queryset:
            json_path = os.path.join(settings.BASE_DIR, 'media', 'data', f'{asset.serial_number}_timing_data.json')
            if os.path.exists(json_path):
                with open(json_path) as f:
                    json_data = json.load(f)
                    for entry in json_data.get('entries', []):
                        timing_logs.append({
                            'serial_number': asset.serial_number,
                            'dise_code': dise_code,
                            'date': entry.get('date'),
                            'start_time': entry.get('start_time'),
                            'end_time': entry.get('end_time'),
                            'duration': entry.get('duration'),
                            'school': asset.dise.school_name,
                            'block': asset.dise.block,
                        })
    request.session['timing_logs'] = timing_logs

    return render(request, 'monitor/reportDevicetime.html', {
        'queryset': queryset,
        'districts': districts,
        'blocks': blocks,
        'villages': villages,
        'schools': schools,
        'serials': serials,
        'selected_district': selected_district,
        'selected_block': selected_block,
        'selected_village': selected_village,
        'selected_school': selected_school,
        'selected_serial': selected_serial,
        'fdate': fdate,
        'tdate': tdate,
        'timing_logs': timing_logs,
        'timeperiod': timeperiod,
        'dise_code': dise_code,
    })


def school(request):
    selected_district = request.POST.get('district', '').strip()
    selected_block = request.POST.get('block', '').strip()
    selected_village = request.POST.get('village', '').strip()
    selected_school = request.POST.get('school', '').strip()
    dise_code = request.POST.get('dise', '').strip()
    page_number = int(request.POST.get('page', 0))

    # Clear button clicked
    if 'clear' in request.POST:
        selected_district = ''
        selected_block = ''
        selected_village = ''
        selected_school = ''
        dise_code = ''
        page_number = 0

    # Start with all schools
    queryset = School.objects.all()

    # Apply filters
    if selected_school:
        queryset = queryset.filter(school_name=selected_school)
    elif selected_village:
        queryset = queryset.filter(village=selected_village)
    elif selected_block:
        queryset = queryset.filter(block=selected_block)
    elif selected_district:
        queryset = queryset.filter(district=selected_district)
    elif dise_code:
        queryset = queryset.filter(dise_code=dise_code)

    # Total count and pagination
    total = queryset.count()
    paginator = Paginator(queryset, 100)
    page_obj = paginator.get_page(page_number + 1)

    # Dropdowns
    districts = School.objects.values_list('district', flat=True).distinct().order_by('district')
    blocks = School.objects.filter(district=selected_district).values_list('block', flat=True).distinct().order_by('block') if selected_district else []
    villages = School.objects.filter(block=selected_block).values_list('village', flat=True).distinct().order_by('village') if selected_block else []
    schools = School.objects.filter(village=selected_village).values_list('school_name', flat=True).distinct().order_by('school_name') if selected_village else []

    return render(request, 'monitor/school.html', {
        'table_data': page_obj.object_list,  # ✅ Must pass this for the table
        'tot': total,
        'page': page_number,
        'startPage': page_number == 0,
        'endPage': page_number + 1 >= paginator.num_pages,
        'districts': districts,
        'blocks': blocks,
        'villages': villages,
        'schools': schools,
        'selected_district': selected_district,
        'selected_block': selected_block,
        'selected_village': selected_village,
        'selected_school': selected_school,
        'dise': dise_code,
    })

from django.db.models import Prefetch

def livestatus(request):
    selected_district = request.POST.get('district', '').strip()
    selected_block = request.POST.get('block', '').strip()
    selected_village = request.POST.get('village', '').strip()
    selected_school = request.POST.get('school', '').strip()
    selected_status = request.POST.get('status', '').strip()
    page_number = int(request.POST.get('page', 0))
    # In your livestatus view, after getting page_obj.object_list
    sr_number = 1
    # Base queryset
    schools = School.objects.all()

    # Apply school filters
    if selected_school:
        schools = schools.filter(school_name=selected_school)
    elif selected_village:
        schools = schools.filter(village=selected_village)
    elif selected_block:
        schools = schools.filter(block=selected_block)
    elif selected_district:
        schools = schools.filter(district=selected_district)

    # Prefetch related assets filtered by selected status
    if selected_status:
        filtered_assets = Asset.objects.filter(status__iexact=selected_status)
    else:
        filtered_assets = Asset.objects.all()

    schools = schools.prefetch_related(
        Prefetch('asset_set', queryset=filtered_assets, to_attr='filtered_assets')
    )

    # Only keep schools with at least one matching asset
    filtered_schools = [s for s in schools if hasattr(s, 'filtered_assets') and s.filtered_assets]

    # Paginate schools
    paginator = Paginator(filtered_schools, 100)
    page_obj = paginator.get_page(page_number + 1)
    for school in page_obj.object_list:
       if hasattr(school, 'filtered_assets'):
            for asset in school.filtered_assets:
                asset.sr_no = sr_number
                sr_number += 1

    # Dropdown data
    districts = School.objects.values_list('district', flat=True).distinct().order_by('district')
    blocks = School.objects.filter(district=selected_district).values_list('block', flat=True).distinct().order_by('block') if selected_district else []
    villages = School.objects.filter(block=selected_block).values_list('village', flat=True).distinct().order_by('village') if selected_block else []
    schools_list = School.objects.filter(village=selected_village).values_list('school_name', flat=True).distinct().order_by('school_name') if selected_village else []

    return render(request, 'monitor/livestatus.html', {
        'table_data': page_obj.object_list,
        'tot': sr_number-1,
        'page': page_number,
        'startPage': page_number == 0,
        'endPage': page_number + 1 >= paginator.num_pages,
        'districts': districts,
        'blocks': blocks,
        'villages': villages,
        'schools': schools_list,
        'selected_district': selected_district,
        'selected_block': selected_block,
        'selected_village': selected_village,
        'selected_school': selected_school,
        'status': selected_status,
        'has_matching_assets': len(filtered_schools) > 0,
    })

def regInfo(request):
    data = []
    tot = 0

    # Get POST selections (even if it's just a dropdown change)
    selected_district = request.POST.get('district', '').strip()
    selected_block = request.POST.get('block', '').strip()
    selected_village = request.POST.get('village', '').strip()
    selected_school = request.POST.get('school', '').strip()
    dise_code = request.POST.get('dise', '').strip()
    asset_input = request.POST.get('asset', '').strip()
    fdate = request.POST.get('fdate', '').strip()
    tdate = request.POST.get('tdate', '').strip()

    # Dropdown options
    districts = School.objects.values_list('district', flat=True).distinct().order_by('district')
    blocks = School.objects.filter(district=selected_district).values_list('block', flat=True).distinct().order_by('block') if selected_district else []
    villages = School.objects.filter(block=selected_block).values_list('village', flat=True).distinct().order_by('village') if selected_block else []
    schools = School.objects.filter(village=selected_village).values_list('school_name', flat=True).distinct().order_by('school_name') if selected_village else []

    # If form submitted via "Generate" button
    if request.method == "POST" and 'clear' in request.POST:
        return render(request, 'monitor/regInfo.html', {
        'asset_list': [],
        'tot': 0,
        'districts': School.objects.values_list('district', flat=True).distinct().order_by('district'),
        'blocks': [],
        'villages':[],
        'schools': [],
        'selected_district': ' ',
        'selected_block': ' ',
        'selected_village': ' ',
        'selected_school': ' ',
        'fdate': ' ',
        'tdate': ' ',
    })
    if request.method == "POST" and 'generate' in request.POST:
        data = Asset.objects.select_related('dise').all()

        if dise_code:
            data = data.filter(dise__dise_code__icontains=dise_code)
        if selected_district and selected_district != "Please Select":
            data = data.filter(dise__district__icontains=selected_district)
        if selected_block:
            data = data.filter(dise__block__icontains=selected_block)
        if selected_village:
            data = data.filter(dise__village__icontains=selected_village)
        if selected_school:
            data = data.filter(dise__school_name__icontains=selected_school)
        if fdate and tdate:
            data = data.filter(date__range=[fdate, tdate])
        if asset_input:
            data = data.filter(
                Q(serial_number__icontains=asset_input) |
                Q(webcam__icontains=asset_input) |
                Q(tft__icontains=asset_input) |
                Q(headphone__icontains=asset_input)
            )

        tot = data.aggregate(total_pc=Count('pc'))['total_pc'] or 0
    else:
        # Just show filtered dropdowns; don't reload all data
        data = Asset.objects.select_related('dise').all()
        tot = data.aggregate(total_pc=Count('pc'))['total_pc'] or 0

    timing_logs = []
    for i, asset in enumerate(data, start=1):
        timing_logs.append({
            'sr': i,
            'dise_code': asset.dise.dise_code,
            'district': asset.dise.district,
            'block': asset.dise.block,
            'village': asset.dise.village,
            'school': asset.dise.school_name,
            'lab': asset.lab,
            'pc': asset.pc,
            'serial_number': asset.serial_number,
            'tft': asset.tft,
            'headphone': asset.headphone,
            'webcam': asset.webcam,
            'switch': asset.switch,
            'date': asset.date.strftime('%d/%m/%Y') if asset.date else ''
        })
    request.session['timing_logs'] = timing_logs
    return render(request, 'monitor/regInfo.html', {
        'asset_list': data,
        'tot': tot,
        'districts': districts,
        'blocks': blocks,
        'villages': villages,
        'schools': schools,
        'selected_district': selected_district,
        'selected_block': selected_block,
        'selected_village': selected_village,
        'selected_school': selected_school,
        'fdate': fdate,
        'tdate': tdate,
    })
def index(request):
    # Total counts
    tot_schl = School.objects.count()
    tot_asset = Asset.objects.count()

    # Device status counts
    active_devices = Asset.objects.filter(status='active').count()
    inactive_devices = tot_asset - active_devices

    # Percentage calculations with zero-division protection
    active_percentage = round((active_devices / tot_asset) * 100, 2) if tot_asset > 0 else 0
    inactive_percentage = round(100 - active_percentage, 2) if tot_asset > 0 else 0

    # Get all districts and their counts
    districts_data = (
        Asset.objects.values('dise__district')
        .annotate(
            total=Count('id'),
            active=Count('id', filter=Q(status='active'))
        )
        .order_by('dise__district')
    )

    # Convert to a dictionary format for easy template access
    district_stats = {
        item['dise__district']: {
            'total': item['total'],
            'active': item['active'],
            'inactive': item['total'] - item['active'],
            'active_percent': round((item['active'] / item['total']) * 100, 2) if item['total'] > 0 else 0
        }
        for item in districts_data
    }

    # Prepare bar chart data - ensure we have data to display
    bar_labels = list(district_stats.keys()) if district_stats else []
    bar_values = [stats['active'] for stats in district_stats.values()] if district_stats else []
    bar_totals = [stats['total'] for stats in district_stats.values()] if district_stats else []

    context = {
        'tot_schl': tot_schl,
        'tot_asset': tot_asset,
        'active_count': active_devices,
        'inactive_count': inactive_devices,
        'active_percentage': active_percentage,
        'inactive_percentage': inactive_percentage,
        'bar_labels': json.dumps(bar_labels),  # Convert to JSON for JavaScript
        'bar_values': json.dumps(bar_values),
        'bar_totals': json.dumps(bar_totals),
        'district_stats': district_stats
    }

    return render(request, 'monitor/index.html', context)
def user_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error = "Invalid username or password"

    return render(request, 'monitor/login.html', {'error': error})
