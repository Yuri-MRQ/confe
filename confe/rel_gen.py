from reportlab.pdfgen import canvas
import tempfile
import os
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table
from collections import OrderedDict
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import pink, black, red, blue, green
import datetime


logo_marinha = '/home/ymquint/programacao/Flask/controles/static/img/marinha.png'


def nivel_agrup1(c, column,value, x, y):
    y = test_limit_pag(x, y)
    c.drawString(x*cm, y*cm, '{}: {}'.format(column, value))
    c.line(2*cm, (y-0.3)*cm, 18*cm, (y-0.3)*cm)
    print(value, y)

    return y

def nivel_agrup2(c, columns, value, x, y, line=True, bold=True):
    y = test_limit_pag(x, y)
    if bold == True:
        c.setFont('Times-Bold', 12)
    else: 
        c.setFont('Times-Roman', 12)
    i = 0
    for column in columns:
        try:
            c.drawString(x*cm, y*cm, '{}: {}'.format(column, value[i]))
        except KeyError as k:
            print(k)
            pass
        
        i +=1
        x += (17.5)/len(columns)
    if line == True:
        c.line(2*cm, (y-0.3)*cm, 18*cm, (y-0.3)*cm)
    
    return y

def nivel_agrup3(c, columns, value, x, y):
    y = test_limit_pag(x, y)
    column_value(c, value, columns, x, y)
    y_final = y - 0.5
    print(value, y)
    return y_final

def nivel_agrup4(c, tipo ,total, y):
    y = test_limit_pag(y=y, x=0)
    s1 = 'Total {}: {}'.format(tipo, total)
    cursormoves1(c, s1, 15, (y-5), 1)

    return y

def footer(c, nip, nome):
    c.drawString(8*cm, 0.5*cm, 'Relatório gerado por: {} {}'.format(nip, nome))

def column_value(c, values, columns, x, y):
    y = test_limit_pag(x, y)
    i = 0
    for column in columns:
        c.drawCentredString(x*cm, y*cm, column)
        c.drawCentredString(x*cm, (y-0.5)*cm, str(values[i]))
        i += 1
        x += (17.5)/len(columns)
    return y

def cursormoves1(canvas, text, x, y, wordspace):

    y = test_limit_pag(x, y)
    canvas.setFont('Times-Roman', 12)
    textobject = canvas.beginText()
    textobject.setTextOrigin(x*cm, y*cm)
    textobject.setWordSpace(wordspace)
    textobject.textLine(text)
    canvas.drawText(textobject)

    return y

def layout_rel(nome_docu):
    path = '/tmp/{}.pdf'.format(nome_docu)
    c = canvas.Canvas(path)
    c.setPageSize(A4)
    c.setFont('Times-Bold', 12)
    c.drawInlineImage(logo_marinha, 8.5*cm, 25.1*cm, 4*cm, 4*cm)
    c.drawCentredString(10.49*cm, 24.5*cm, 'MARINHA DO BRASIL')
    c.drawCentredString(10.49*cm, 23.5*cm, 'GRUPAMENTO DE NAVIOS HIDROCEANOGRÁFICOS')
    c.drawCentredString(10.49*cm, 22.5*cm, 'RELATÓRIO {}'.format(nome_docu.upper()))

    return c, path

def test_limit_pag(x, y):
    # o objetivo é ver se o y, x recebido está dentro do limite da página
    x_max = 20.995
    y_max = 28.4

    if y > y_max:
        y -= y - y_max
    if x > x_max:
        x -= x - x_max

    return y