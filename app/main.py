import fitz
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
from tabula import read_pdf
import os
os.environ['JAVA_HOME'] = '/usr'

def convertir_a_json_compatible(data):
    if isinstance(data, list):
        return [convertir_a_json_compatible(item) for item in data]
    elif isinstance(data, dict):
        return {convertir_a_json_compatible(key): convertir_a_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, float):
        return round(data, 2)  # Redondear los valores float a 2 decimales
    else:
        return data

app = FastAPI()

@app.get('/', response_class=HTMLResponse)
async def index():
    return """
  <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Roboto+Mono:wght@400;500&family=Roboto+Slab:wght@500;600&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="" type="text/css">
    <title>Plenty APP</title>
</head>
<body>
    <div class="container">
        <h1>PLENTY APP - MODULO ADMINISTRATIVO</h1>
        <h3>Sección: Carga de Facturas</h3>
        <div class="view">
            <h4></h4>
            <!-- <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="pdfFile">
                <input id="button" type="submit" value="upload">
            </form> -->
            <form action="/upload" method="post" enctype="multipart/form-data">
              <input type="file" name="pdf_file" accept=".pdf">
              <input type="submit" value="Subir PDF">
          </form>
        </div>

    </div>
</body>
</html>
    """

def convertir_a_json_compatible(data):
    if isinstance(data, list):
        return [convertir_a_json_compatible(item) for item in data]
    elif isinstance(data, dict):
        return {convertir_a_json_compatible(key): convertir_a_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, float):
        if data < 1e308 and data > -1e308:  # Verificar si el valor está dentro del rango permitido
            return round(data, 2)  # Redondear los valores float a 2 decimales
        else:
            return str(data)  # Convertir el valor a una cadena si está fuera de rango
    else:
        return data

@app.post("/upload/")
async def upload_file(pdf_file: UploadFile = File(...)):
    try:
        print(f"Recibido archivo: {pdf_file.filename}")
        
        if not pdf_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")
        
        # Guardar el archivo en el sistema
        pdf_path = f'uploads/{pdf_file.filename}'
        with open(pdf_path, 'wb') as buffer:
            buffer.write(pdf_file.file.read())
        
     

        # Extraer texto del PDF
        # doc = fitz.open(pdf_path)
        # text = ""
        # for page in doc:
        #     page_text = page.get_text()
        #     page_text = page_text.replace('Fechas de viaje', '').replace('*Última noche de alojamiento en el hotel.', '')
        #     text += page_text
        # doc.close()

      

        # Extraer tablas
        tables = read_pdf(pdf_path, pages='all', multiple_tables=True)

        table_data = []
        for table in tables:
            table_data.append(convertir_a_json_compatible(table.to_dict()))
     

        return {'tables': table_data }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)