from flask import Flask, request, jsonify, render_template_string, send_file
import pandas as pd
import google.generativeai as genai
import nbformat as nbf
import re
import io

# API Ayarları
API_KEY = "GEMINI_API_KEY_HERE"
genai.configure(api_key=API_KEY)

app = Flask(__name__)

# Modeli tanımlıyoruz
model = genai.GenerativeModel('gemini-2.5-flash')

@app.route('/', methods=['GET'])
def home():
    html_form = """
    <!doctype html>
    <html lang="tr">
    <head>
        <meta charset="utf-8">
        <title>AI EDA - Notebook Üretici</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; max-width: 600px; margin: 0 auto; }
            .upload-box { border: 2px dashed #ccc; padding: 20px; text-align: center; border-radius: 10px; }
            button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 15px;}
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h2>Veri Analizi ve Notebook Üretimi</h2>
        <div class="upload-box">
            <form action="/api/analyze" method="post" enctype="multipart/form-data">
                <p>Analiz edilecek CSV dosyasını seçin:</p>
                <input type="file" name="file" accept=".csv" required><br>
                <button type="submit">İncele ve .ipynb İndir</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_form)

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    if 'file' not in request.files:
        return jsonify({'error': 'Lütfen bir dosya yükleyin.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Seçili dosya yok.'}), 400

    try:
        # 1. Veri Özeti
        df = pd.read_csv(file)
        metadata = {
            "toplam_satir": len(df),
            "kolonlar": list(df.columns),
            "veri_tipleri": df.dtypes.astype(str).to_dict(),
            "eksik_degerler": df.isnull().sum().to_dict(),
        }
        
        # 2. LLM Promptu
        prompt = f"""
        Sen dünya standartlarında bir Veri Bilimcisi ve Görselleştirme Uzmanısın. Amacın, verilen CSV özetini (metadata) kullanarak, Jupyter Notebook ortamında görsel olarak büyüleyici, okunması keyifli ve en derin içgörüleri sağlayan 4 gelişmiş Plotly grafiği üretmek.

        Veri seti halihazırda 'df' adlı pandas DataFrame içindedir.

        [JUPYTER NOTEBOOK TASARIM VE FORMAT KURALLARI - ÇOK ÖNEMLİ]
        1. İLK HÜCRE (GİRİZGAH): En başa KESİNLİKLE büyük ve renkli bir ana başlık ekle. HTML kullan. Örn: <h1 style="color: #2E86C1; text-align: center;">📊 Yapay Zeka Destekli Keşifsel Veri Analizi (EDA)</h1>
        2. GİRİZGAH İÇERİĞİ: Başlığın hemen altına verinin neyle ilgili olduğuna dair vizyoner bir açıklama yaz. Ardından analiz boyunca hangi grafiklerin çizileceğini anlatan şık bir "İçindekiler" (Table of Contents) listesi ekle.
        3. BAŞLIK HİYERARŞİSİ VE RENKLER: 
        - Ana konu/grafik başlıkları için büyük ve dikkat çekici HTML kullan: <h2 style="color: #E74C3C;">...</h2>
        - Alt başlıklar veya bilgi notları için: <h3 style="color: #F39C12;">...</h3>
        4. AÇIKLAMALAR: Normal yazılması gereken metinleri standart Markdown ile yaz, ancak metin içindeki KÖK NEDENLERİ, İSTATİSTİKLERİ veya ÖNEMLİ VURGULARI kesinlikle <span style="color: #27AE60; font-weight: bold;">renkli ve kalın</span> yazarak belirginleştir.

        [GÖRSELLEŞTİRME KURALLARI]
        1. Veride tarih/zaman veya ardışık veri varsa KESİNLİKLE 'Time Series Line Chart' veya 'Area Chart' çiz.
        2. Kategorik değişkenler ve sayısal değerler bir aradaysa basit Bar Chart yerine 'Sunburst Chart', 'Treemap' veya 'Violin Plot' kullan.
        3. Değişkenler arası korelasyonu göstermek için KESİNLİKLE bir 'Heatmap' veya '3D Scatter Plot' ekle.
        4. Çizilen her grafiğin teması karanlık (template='plotly_dark') olsun ve başlıkları ortalanmış (title_x=0.5) olsun.
        5. KRİTİK KURAL: `px.parallel_categories` veya benzeri renk bekleyen grafikler çizeceksen ve 'color' parametresine kategorik bir string kolonu vereceksen, KESİNLİKLE öncesinde `pd.Categorical(df['KolonAdı']).codes` kullanarak o kolonu sayısallaştır!

        İşte Veri Özeti:
        {metadata}

        LÜTFEN ŞU FORMATA KESİNLİKLE UY:
        - Asla JSON veya raw notebook formatı üretme. Sadece Markdown (ve HTML etiketleri) formatında yaz.
        - İşleyiş sırası: Girizgah -> Renkli Açıklama -> ```python kod ``` -> Renkli Açıklama -> ```python kod ``` şeklinde olmalıdır.
        """
        
        response = model.generate_content(prompt)
        llm_markdown_output = response.text
        
        # 3. Markdown çıktısını Jupyter Notebook'a Çevirme
        nb = nbf.v4.new_notebook()
        
        # Regex ile kod bloklarını ve metinleri ayırıyoruz
        # ```python ve ``` arasındaki her şeyi kod olarak, geri kalanları metin olarak algılar
        parts = re.split(r'```python\n(.*?)\n```', llm_markdown_output, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
                
            if i % 2 == 0:
                # Çift sayılar (0, 2, 4...) Markdown metinlerine denk gelir
                nb['cells'].append(nbf.v4.new_markdown_cell(part))
            else:
                # Tek sayılar (1, 3, 5...) Regex'in yakaladığı Python kodlarına denk gelir
                nb['cells'].append(nbf.v4.new_code_cell(part))

        # 4. Notebook dosyasını bellekte oluştur ve kullanıcıya indirt
        nb_io = io.StringIO()
        nbf.write(nb, nb_io)
        
        mem = io.BytesIO()
        mem.write(nb_io.getvalue().encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='application/x-ipynb+json',
            as_attachment=True,
            download_name='ai_veri_analizi.ipynb'
        )
        
    except Exception as e:
        return jsonify({'error': f'Hata oluştu: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)