import fitz  # PyMuPDF

def open_pdf(file_path):
    """
    Opent een PDF en retourneert alle tekstinhoud.
    :param file_path: pad naar het PDF-bestand
    :return: string met alle tekst
    """
    text = ""
    try:
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        print(f"[OK] PDF succesvol gelezen: {file_path}")
    except Exception as e:
        print(f"[FOUT] Kon PDF niet lezen: {e}")
    return text
