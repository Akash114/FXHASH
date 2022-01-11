from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from decimal import Decimal
import time
import pandas as pd
import multiprocessing
from multiprocessing import Manager
import inspect
from multiprocessing.pool import ThreadPool as Pool

minted = 0
total = 1


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    if request.method == 'POST':
        ip = get_client_ip(request)
        id = request.POST.get('id')
        password = request.POST.get('pass')
        if ip in request.session:
            num = request.session[ip]
            if num >= 1:
                request.session['login'] = 'success'
                return render(request,'login.html',{'msg': "Too Many Wrong Attempts"})
        if id == 'FxHashMint' and password == 'mintToken@fxhash@421':
            return render(request,'mint.html')
        else:
            if ip not in request.session:
                request.session[ip] = 0
            request.session[ip] += 1

            return render(request, 'login.html', {'msg': "Too Many Wrong Attempts"})


def index(request):
    if 'login' in request.session:
        return render(request, 'mint.html')
    else:
        return render(request,'login.html')


def mint_request(request):
    if request.method == 'POST':
        from pytezos import pytezos
        key = request.POST.get('key')
        token_key = request.POST.get('token_key')
        price = Decimal(request.POST.get('price'))
        number = int(request.POST.get('number'))
        gas = request.POST.get('gas_type')
        gas_limit = {
            'low': 19000,
            'moderate': 24000,
            'high': 30000
        }
        global total
        total = number
        pytezos = pytezos.using(
            key=key,
            shell='https://mainnet.api.tez.ie')
        contract = pytezos.contract('KT1XCoGnfupWk7Sp8536EfrxcP73LmT68Nyr')
        args = (contract, token_key, price, number,gas_limit[gas])
        msg = task(args)
        return JsonResponse({
            'msg': msg
        })


def task(args):
    global minted
    status = []
    for i in range(args[3]):
        try:
            print(args[0].mint(int(args[1])).with_amount(Decimal(args[2])).as_transaction(gas_limit=int(args[4])).send())
            #print(args[0].mint(args[1]).with_amount(args[2]).operation_group.fill({'gas_limit':int(args[4])}))
            print("Thread is running")
            time.sleep(15)
            minted += 1
            msg = str(args[1]) + ' :- ' + str(i+1) + ' Minted Successfully <br/>'
        except Exception as e:
            print(e)
            msg = str(args[1]) + ' :- ' + str(i+1) + ' Minted with an error :- ' + str(e) + "<br/>"

        status.append(msg)
    return status


def mint_multiple(request):
    if request.method == 'POST':
        file = request.FILES['csv-file']
        df = pd.read_csv(file)
        global total
        total = df['Numbers Of Tokens'].sum()
        inputs = []
        gas_limit = {
            'low':19000,
            'moderate':24000,
            'high':30000
        }
        gas = request.POST.get('gas_type')

        for index, row in df.iterrows():
            from pytezos import pytezos
            pytezos = pytezos.using(
                key=row['Private Key'],
                shell='https://mainnet.api.tez.ie')
            contract = pytezos.contract('KT1XCoGnfupWk7Sp8536EfrxcP73LmT68Nyr')
            args = (contract, row['Token ID'], row['Token Price'], row['Numbers Of Tokens'],gas_limit[gas])
            inputs.append(args)

        pool = Pool()

        outputs = pool.map(task, inputs)
        print(outputs)
        data = ''
        for elements in outputs:
            for element in elements:
                data += element + '\n'

        print(outputs)
        return JsonResponse({
            'msg': 'Minting is Completed...',
            'data':data
        })


def update_process(request):
    global minted
    if minted == total:
        minted = 0
        return JsonResponse({
            'update_progress': 100
        })

    return JsonResponse({
        'update_progress': (minted / total) * 100
    })
