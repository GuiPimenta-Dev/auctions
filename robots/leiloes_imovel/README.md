# Leiloes Imovel Robot

This is a standalone Python robot that scrapes property auctions from leilaoimovel.com.br based on user preferences and saves the results to Google Sheets.

## Features

- Search for properties based on:
  - Property types (house, apartment, etc.)
  - State and city
  - Neighborhoods
  - Budget
- Automatically handles Cloudflare protection
- Fuzzy matching for city and neighborhood names
- Saves results to Google Sheets
- Reads client preferences from Google Sheets
- Prevents duplicate entries

## Installation

1. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Google Sheets:

   - Create a new Google Sheet named "Leilões Imóveis"
   - Create a worksheet named "Clientes" with the following columns:
     - Nome Completo
     - Tipo de imóvel
     - Estado de interesse
     - Cidade de interesse
     - Bairros de interesse
     - Valor de orçamento destinado ao investimento

4. Set up Google Service Account:
   - Create a service account in Google Cloud Console
   - Download the service account credentials JSON
   - Set the credentials as an environment variable:
   ```bash
   export GOOGLE_CREDENTIALS='{"type": "service_account", ...}'
   ```

## Usage

1. Add your client data to the "Clientes" worksheet in Google Sheets
2. Run the robot:

```bash
python main.py
```

The robot will:

1. Read client preferences from the "Clientes" worksheet
2. Search for properties matching each client's criteria
3. Save found properties to the "Leilões" worksheet
4. Skip any properties that have already been saved for that client

## Google Sheets Structure

### Clientes Worksheet

- Nome Completo: Client's full name
- Tipo de imóvel: Property types (comma-separated)
- Estado de interesse: State of interest
- Cidade de interesse: City of interest
- Bairros de interesse: Neighborhoods of interest (comma-separated)
- Valor de orçamento destinado ao investimento: Budget in Brazilian currency format

### Leilões Worksheet

The robot will automatically create this worksheet with the following columns:

- Nome do Cliente
- Nome do Imóvel
- Tipo
- Modalidade
- Estado
- Cidade
- Endereço
- Bairro
- Valor de Avaliação
- Valor com Desconto
- Área (m²)
- Quartos
- Vagas
- URL da Imagem
- URL do Imóvel
- URL da Busca
- Data do Leilão
- Valor do Leilão
- Data da Segunda Proposta
- Valor da Segunda Proposta

## Notes

- The robot uses fuzzy matching to find cities and neighborhoods, so slight misspellings are tolerated
- Property types can be combined using commas (e.g., "casa, apartamento")
- The budget should be provided in Brazilian currency format (e.g., "500.000,00")
- The robot automatically handles pagination and will fetch all available results
- Duplicate properties are automatically skipped for each client
