# Create your views here.
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect
import re
from django.shortcuts import render_to_response
from django.template import RequestContext
from check import forms
import pymarc


def home(request):
    if request.method == 'GET':
        form = forms.MarcUploadForm()
        return render_to_response('home.html', {'form':form}, context_instance=RequestContext(request))
    if request.method == 'POST':
        f = forms.MarcUploadForm(request.POST, request.FILES)
        if f.is_valid():
            res = {}
            filename = request.FILES['filename']
            file = filename.read()
            #field = f.cleaned_data['marcfield']
            try:
                reader = pymarc.MARCReader(file)
                for record in reader:
                    res[record.isbn()] = {}
                    res[record.isbn()]['title'] = record.title()
                    if record.leader[5] not in ('c','n'):
                        res[record.isbn()]['Status'] = record.leader[5]

                    if record.leader[6] != 'a':
                        res[record.isbn()]['Type'] = record.leader[6]

                    if record.leader[7] != 'm':
                        res[record.isbn()]['Blvl'] = record.leader[7]

                    if record.leader[17] in ('2','3','5','7','8','E','J','K','M'):
                        res[record.isbn()]['Encoding'] = record.leader[17]

                    if record['040']['b'] and record['040']['b'] != 'eng':
                        res[record.isbn()]['040b'] = record['040']['b']

                    if re.search(r"\d{4}",record['050'].__str__()[-4]):
                        res[record.isbn()]['050'] = record['050'].__str__()

                    if re.search(r"\d{4}",record['090'].__str__()[-4]):
                        res[record.isbn()]['090'] = record['090'].__str__()

                    if record['245']['n']:
                        res[record.isbn()]['245n'] = record['245']['n'].__str__()

                    if record['245']['p']:
                        res[record.isbn()]['245p'] = record['245']['p'].__str__()

                    if re.search(r"\d+",record['245']['a'].__str__()):
                        res[record.isbn()]['245a'] = record['245']['a']

                    if re.search(r"\d+",record['245']['b'].__str__()):
                        res[record.isbn()]['245b'] = record['245']['b']

                    if re.search(r"annual|biennial",record['245'].__str__()):
                        res[record.isbn()]['245b'] = record['245']['b']

                    if not record['300']:
                        res[record.isbn()]['300'] = "Missing"

                    else:
                        if record['300']['e']:
                            res[record.isbn()]['300e'] = record['300']['e'].__str__()

                        if re.match(r'p.|v.|pages',record['300']['a'].__str__()):
                            res[record.isbn()]['300a'] = record['300']['a'].__str__()

                    if record['490'] and record['490'].indicator1 and record['490'].indicator1 == '0':
                        res[record.isbn()]['490'] = "First indicator was 0"

                    for field in record:
                        if field.is_subject_field() and field.indicator2 and field.indicator2 == '0':
                            del res[record.isbn()]['6xx']
                            break;
                        else:
                            res[record.isbn()]['6xx'] = "No 6xx records contain second indicator 0"
            except IOError:
                pass


            return render_to_response('results.html', {'results':res})

def reports(request):
    return render_to_response('reports.html')


