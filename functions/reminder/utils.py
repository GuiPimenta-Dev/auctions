from pprint import pprint

from datetime import datetime



def quadrimestre_atual():
    year = datetime.utcnow().year
    month = datetime.utcnow().month
    quarter = (month - 1) // 4 + 1
    return f"{year} Q{quarter}"


def consulta_pressao_vista():
  import requests

  url = f"https://observatorio.sinnc.app/esus_indicadores_filter/Indicadores/6|Niterói - RJ - 3303302|{quadrimestre_atual()}||2282232|0000296015|ATIVO|Não informado;Óbito;Mudança de território"

  payload = ""
  headers = {
      "Accept": "*/*",
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://observatorio.sinnc.app/esus_indicador_6/",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "sec-ch-ua-mobile": "?0",
      "Cookie": "csrftoken=eEQL0dLx4K6pu0USofSVYex6uVZyzjXs; sessionid=l0v3y90cypz7x3u1d7kp4eanumigjfcr"
  }

  response = requests.request("GET", url, data=payload, headers=headers)

  return response.json()

def consulta_de_hipertensao():
  import requests

  url = "https://observatorio.sinnc.app/pmf_indicador6_get_data/getDataTablePacientes"

  querystring = {"quadrimestre": quadrimestre_atual(),"unidade":"2282232","equipe":"0000296015"}

  payload = ""
  headers = {
      "Accept": "*/*",
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://observatorio.sinnc.app/pmf_indicador6/",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "sec-ch-ua-mobile": "?0",
      "Cookie": "csrftoken=eEQL0dLx4K6pu0USofSVYex6uVZyzjXs; sessionid=l0v3y90cypz7x3u1d7kp4eanumigjfcr"
  }

  response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

  return response.json()


def consulta_hemoglobina_glicada():
  import requests

  url = f"https://observatorio.sinnc.app/esus_indicadores_filter/Indicadores/7|Niterói - RJ - 3303302|{quadrimestre_atual()}||2282232|0000296015|ATIVO|Não informado;Óbito;Mudança de território"

  payload = ""
  headers = {
      "Accept": "*/*",
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://observatorio.sinnc.app/esus_indicador_7/",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "sec-ch-ua-mobile": "?0",
      "Cookie": "csrftoken=eEQL0dLx4K6pu0USofSVYex6uVZyzjXs; sessionid=l0v3y90cypz7x3u1d7kp4eanumigjfcr"
  }

  response = requests.request("GET", url, data=payload, headers=headers)

  return response.json()

def consulta_diabetes():
  import requests

  url = "https://observatorio.sinnc.app/pmf_indicador7_get_data/getDataTablePacientes"

  querystring = {"quadrimestre": quadrimestre_atual(),"unidade":"2282232","equipe":"0000296015"}

  payload = ""
  headers = {
      "Accept": "*/*",
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://observatorio.sinnc.app/pmf_indicador7/",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "sec-ch-ua-mobile": "?0",
      "Cookie": "csrftoken=eEQL0dLx4K6pu0USofSVYex6uVZyzjXs; sessionid=l0v3y90cypz7x3u1d7kp4eanumigjfcr"
  }

  response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

  return response.json()

def consulta_gestantes():
  import requests

  url = f"https://observatorio.sinnc.app/esus_indicadores_filter/Indicadores/1|Niterói - RJ - 3303302|{quadrimestre_atual()}|||0000296015|ATIVO|Não informado;Óbito;Mudança de território"

  payload = ""
  headers = {
      "Accept": "*/*",
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://observatorio.sinnc.app/esus_indicador_1/",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "sec-ch-ua-mobile": "?0",
      "Cookie": "csrftoken=eEQL0dLx4K6pu0USofSVYex6uVZyzjXs; sessionid=l0v3y90cypz7x3u1d7kp4eanumigjfcr"
  }

  response = requests.request("GET", url, data=payload, headers=headers)

  return response.json()
  
def exame_gestante():
  import requests

  url = f"https://observatorio.sinnc.app/esus_indicadores_filter/Indicadores/2|Niterói - RJ - 3303302|{quadrimestre_atual()}|||0000296015|ATIVO|Não informado;Óbito;Mudança de território"

  payload = ""
  headers = {
      "Accept": "*/*",
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://observatorio.sinnc.app/esus_indicador_2/",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "sec-ch-ua-mobile": "?0",
      "Cookie": "csrftoken=eEQL0dLx4K6pu0USofSVYex6uVZyzjXs; sessionid=l0v3y90cypz7x3u1d7kp4eanumigjfcr"
  }

  response = requests.request("GET", url, data=payload, headers=headers)

  return response.json()

def vacina_crianca():
  import requests

  url = "https://observatorio.sinnc.app/esus_indicadores_filter/Indicadores/5%7CNiter%C3%B3i%20-%20RJ%20-%203303302%7C2025%20Q1%7C%7C%7C0000296015%7CATIVO%7CN%C3%A3o%20informado;%C3%93bito;Mudan%C3%A7a%20de%20territ%C3%B3rio"

  payload = ""
  headers = {
      "Accept": "*/*",
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Pragma": "no-cache",
      "Referer": "https://observatorio.sinnc.app/esus_indicador_5/",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
      "sec-ch-ua-mobile": "?0",
      "Cookie": "csrftoken=eEQL0dLx4K6pu0USofSVYex6uVZyzjXs; sessionid=l0v3y90cypz7x3u1d7kp4eanumigjfcr"
  }

  response = requests.request("GET", url, data=payload, headers=headers)
  return response.json()
