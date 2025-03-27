```json
{
    "$schema": "https://gobl.org/draft-0/bill/invoice",
    "$regime": "PT",
    "$addons": [
      "pt-saft-v1"
    ],
    "uuid": "0193f36f-9fda-7000-9aff-4f4e28043a66",
    "type": "standard",
    "series": "FT SERIES-A",
    "issue_date": "2024-12-23",
    "currency": "EUR",
    "supplier": {
      "name": "Innovatech Lda",
      "tax_id": {
        "country": "PT",
        "code": "770013813"
      },
      "addresses": [
        {
          "street": "Rua das Flores 200 3º Esquerdo",
          "locality": "Porto",
          "code": "4050-265",
          "country": "PT"
        }
      ]
    },
    "customer": {
      "name": "Gusto Unipessoal Lda",
      "tax_id": {
        "country": "PT",
        "code": "514329874"
      },
      "addresses": [
        {
          "street": "Avenida da Liberdade 152 2º Direito",
          "locality": "Lisboa",
          "code": "1250-146",
          "country": "PT"
        }
      ],
      "emails": [
        {
          "addr": "gusto@example.com"
        }
      ],
      "websites": [
        {
          "url": "https://gusto.example.com"
        }
      ],
      "telephones": [
        {
          "num": "+351912345678"
        }
      ]
    },
    "lines": [
      {
        "i": 1,
        "quantity": "20.0",
        "item": {
          "name": "Development services",
          "price": "50.00",
          "unit": "h"
        },
        "taxes": [
          {
            "cat": "VAT",
            "rate": "standard"
          }
        ]
      }
    ],
    "payment": {
      "advances": [
        {
          "date": "2024-12-23",
          "key": "card",
          "description": "Advance payment",
          "amount": "12.34"
        }
      ]
    }
}
```