from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from monitor.models import School, Asset
from datetime import date,datetime, timedelta
from urllib.parse import urlencode
import random
import string
from django.contrib import messages
import json
import os

def generate_serial_number():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=10))

def home(request):
    return render(request, 'admin_ui/home.html')

def insert_view(request):
    form_data = {
        'district': request.GET.get('district', ''),
        'block': request.GET.get('block', ''),
        'village': request.GET.get('village', ''),
        'school': request.GET.get('school', ''),
        'serial_number': request.GET.get('serial_number', ''),
        'lab': request.GET.get('lab', ''),
    }
    context = {
        'current_date': date.today().strftime('%Y-%m-%d'),
        'form_data': form_data
    }
    return render(request, 'admin_ui/insert.html', context)

def update_view(request):
    form_data = {
        'district': request.GET.get('district', ''),
        'block': request.GET.get('block', ''),
        'village': request.GET.get('village', ''),
        'school': request.GET.get('school', ''),
    }
    return render(request, 'admin_ui/update.html', {'form_data': form_data})

def delete_view(request):
    return render(request, 'admin_ui/delete.html')

def load_school_data(request):
    if request.method == 'POST':
        dise_code = request.POST.get('dise_code')
        request.session['current_dise_code'] = dise_code
        try:
            school = School.objects.get(dise_code=dise_code)
            new_serial = generate_serial_number()
            query_params = urlencode({
                'district': school.district,
                'block': school.block,
                'village': school.village,
                'school': school.school_name,
                'serial_number': new_serial,
                'lab': request.POST.get('lab', ''),
            })
            return redirect(f'/admin-site/insert/?{query_params}')
        except School.DoesNotExist:
            return JsonResponse("Invalid Dise code: School not found", safe=False)
    return redirect('/admin-site/insert/')

def insert_data(request):
    if request.method == 'POST':
        try:
            dise_code = request.session.get('current_dise_code')
            if not dise_code:
                return render(request, 'admin_ui/insert.html', {
                    'error': "DISE code missing.",
                    "current_date" : date.today().strftime('%d-%m-%Y')
                })

            try:
                school = School.objects.get(dise_code=dise_code)
            except School.DoesNotExist:
                return render(request, 'admin_ui/insert.html', {
                    'error': "School not found for the given DISE code.",
                    "current_date" : date.today().strftime('%d-%m-%Y')
                })
            regDate = request.POST.get('regDate')
            comp_number = request.POST.get('comp_number')
            lab = request.POST.get('lab')
            serial_number = request.POST.get('serial_number')
            tft = request.POST.get('TFT_serial')
            headphone = request.POST.get('Head_serial')
            webcam = request.POST.get('WEB_serial')
            switch = request.POST.get('Switch_serial')
            formatted_date = datetime.strptime(regDate, '%Y-%m-%d').strftime('%d/%m/%Y')
        
            # Calculate timings
            current_run = datetime.now()
            start_time = current_run.strftime('%H:%M:%S')
            start_timestamp = current_run.hour * 3600 + current_run.minute * 60 + current_run.second
            end_time_in_seconds = start_timestamp + 300
            end_time = (datetime.min + timedelta(seconds=end_time_in_seconds)).time().strftime('%H:%M:%S')
            time_diff = end_time_in_seconds - start_timestamp
            duration = (datetime.min + timedelta(seconds=time_diff)).time().strftime('%H:%M:%S')
           
            folder_path = os.path.join('media', 'data')
            os.makedirs(folder_path, exist_ok=True)
                      
            if not comp_number or not comp_number.isdigit() or not (1 <= int(comp_number) <= 15):
                return render(request, 'admin_ui/insert.html', {
                    'error': "Computer number must be between 1 and 15.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })

            if lab not in ['1', '2']:
                return render(request, 'admin_ui/insert.html', {
                    'error': "Lab must be either 1 or 2.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })

            if not serial_number or not tft or not headphone or not webcam or not switch:
                return render(request, 'admin_ui/insert.html', {
                    'error': "All serial number fields are required.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })

            if Asset.objects.filter(dise=school, lab=lab, pc=int(comp_number)).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Computer number {comp_number} already exists in Lab {lab} for this school.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(tft=tft).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"TFT number {tft} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(webcam=webcam).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Webcam Number {webcam} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(headphone=headphone).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Headphone number {headphone} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(switch=switch).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Switch number {switch} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            
            Asset.objects.create(
                dise=school,
                lab=lab,
                pc=int(comp_number),
                serial_number=serial_number,
                tft=tft,
                headphone=headphone,
                webcam=webcam,
                switch=switch,
                date=date.today()
            )
            json_file_path = os.path.join(folder_path, f"{serial_number}_timing_data.json")
            app_file_path = os.path.join(folder_path, f"{serial_number}_app_data.json")

            timing_data = {
                "entries": [{
                    "serial_number": serial_number,
                    "date": formatted_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration
                }]
            }
            app_usage_data = [{
                "package_name": "Unknown Package",
                "date": formatted_date,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration
            }]
            with open(json_file_path, 'w') as f:
                json.dump(timing_data, f, indent=4)
            with open(app_file_path, 'w') as f:
                json.dump(app_usage_data, f, indent=4)
            return redirect('admin_home')

        except Exception as e:
            return render(request, 'admin_ui/insert.html', {
                'error': f"Error: {str(e)}",
                'current_date': date.today().strftime('%Y-%m-%d')
            })

    return redirect('insert')

def loadUpdate_school_data(request):
    if request.method == 'POST':
        serial_number = request.POST.get('serial_number')
        request.session['current_serial_number'] = serial_number
        try:
            asset = Asset.objects.get(serial_number=serial_number)
            school = asset.dise
            query_params = urlencode({
                'district': school.district,
                'block': school.block,
                'village': school.village,
                'school': school.school_name,
            })
            return redirect(f'/admin-site/update/?{query_params}')
        except Asset.DoesNotExist:
            return JsonResponse("Asset not found", safe=False)
    return redirect('/admin-site/update/')

def update_data(request):
    if request.method == 'POST':
        try:
            serial_number = request.session.get('current_serial_number')
            if not serial_number:
                return render(request, 'admin_ui/update.html', {
                    'error': "Serial number is missing in session."
                })

            try:
                asset = Asset.objects.get(serial_number=serial_number)
            except Asset.DoesNotExist:
                return render(request, 'admin_ui/update.html', {
                    'error': "Asset not found with this serial number."
                })

            asset.lab = request.POST.get('lab', asset.lab)
            asset.comp_number = request.POST.get('comp_number', asset.comp_number)
            asset.tft = request.POST.get('TFT_serial', asset.tft)
            asset.headphone = request.POST.get('Head_serial', asset.headphone)
            asset.webcam = request.POST.get('WEB_serial', asset.webcam)
            asset.switch = request.POST.get('Switch_serial', asset.switch)
            asset.save()

            if not asset.comp_number or not asset.comp_number.isdigit() or not (1 <= int(asset.comp_number) <= 15):
                return render(request, 'admin_ui/insert.html', {
                    'error': "Computer number must be between 1 and 15.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })

            if asset.lab not in ['1', '2']:
                return render(request, 'admin_ui/insert.html', {
                    'error': "Lab must be either 1 or 2.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })

            if not serial_number or not asset.tft or not asset.headphone or not asset.webcam or not asset.switch:
                return render(request, 'admin_ui/insert.html', {
                    'error': "All serial number fields are required.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })

            if Asset.objects.filter(dise=asset.school, lab=asset.lab, comp_number=int(asset.comp_number)).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Computer number {asset.comp_number} already exists in Lab {asset.lab} for this school.",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(tft=asset.tft).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"TFT number {asset.tft} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(webcam=asset.webcam).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Webcam Number {asset.webcam} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(headphone=asset.headphone).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Headphone number {asset.headphone} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })
            if Asset.objects.filter(switch=asset.switch).exists():
                return render(request, 'admin_ui/insert.html', {
                    'error': f"Switch number {asset.switch} already exists",
                    'current_date': date.today().strftime('%Y-%m-%d')
                })

            del request.session['current_serial_number']
            return redirect('admin_home')

        except Exception as e:
            return render(request, 'admin_ui/update.html', {
                'error': f"Error: {str(e)}"
            })

    return redirect('update')

def delete_data(request):
    if request.method == 'POST':
        serial_number = request.POST.get('serial_number')
        if not serial_number:
            messages.error(request, "Please provide a serial number")
            return redirect('delete')
        
        try:
            asset = Asset.objects.get(serial_number=serial_number)
            asset.delete()
            folder_path = os.path.join('media', 'data')
            timing_file = os.path.join(folder_path, f'{serial_number}_timing_data.json')
            app_usage_file = os.path.join(folder_path, f'{serial_number}_app_data.json')
                
            if os.path.exists(timing_file):
                os.remove(timing_file)
            if os.path.exists(app_usage_file):
                os.remove(app_usage_file)
            
            messages.success(request, f"Asset with serial number {serial_number} deleted successfully")
            return render(request,'admin_ui/home.html')
        except Asset.DoesNotExist:
            messages.error(request, f"Asset with serial number {serial_number} not found")
            return redirect('delete')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('delete')
    
    return redirect('delete')