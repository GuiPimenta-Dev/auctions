from openpyxl import Workbook

def save_to_excel(results, filename="output.xlsx"):
  wb = Workbook()
  ws = wb.active

  headers = results[0].keys()
  ws.append(list(headers))

  for entry in results:
      ws.append(list(entry.values()))     

  wb.save(filename)