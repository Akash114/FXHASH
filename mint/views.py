from django.http import JsonResponse
from django.shortcuts import render
from pytezos import pytezos


# Create your views here.


def index(request):
    return render(request, 'mint.html')


def mint_request(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        token_key = request.POST.get('token_key')
        price = request.POST.get('price')
        number = request.POST.get('number')
        print(key)
        pytezos = pytezos.using(
            key=key,
            shell='https://mainnet.api.tez.ie')
        contract = pytezos.contract('KT1XCoGnfupWk7Sp8536EfrxcP73LmT68Nyr')
        for i in range(number):
            ATTEMPTS_COUNT = 5
            attempts = 0
            while attempts <= ATTEMPTS_COUNT:
                try:
                    contract.mint(token_key).with_amount(price * 1000000).as_transaction().send()
                    break
                except Exception as e:
                    print(e)
                    attempts += 1
                    if attempts == 5:
                        return JsonResponse({
                            'msg': e
                        })
        return JsonResponse({
            'msg': 'Minting is Completed...'
        })
