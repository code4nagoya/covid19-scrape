import urllib.request
import urllib.error
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO, BytesIO

def convert_pdf(file_url):
    rsrcmgr = PDFResourceManager()
    with StringIO() as retstr:
        codec = 'utf-8'
        laparams = LAParams()
        with TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams) as device:
            f = urllib.request.urlopen(file_url).read()
            with BytesIO(f) as fp:
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                password = ""
                maxpages = 0
                caching = True
                pagenos = set()
                for page in PDFPage.get_pages(fp,
                                            pagenos,
                                            maxpages=maxpages,
                                            password=password,
                                            caching=caching,
                                            check_extractable=True):
                    interpreter.process_page(page)
            fp.close()
        str = retstr.getvalue()
    return str

if __name__ == "__main__":
    print(convert_pdf("https://www.pref.aichi.jp/uploaded/attachment/327109.pdf"))