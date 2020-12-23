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
from rel_gen import (nivel_agrup1, nivel_agrup2, nivel_agrup3, nivel_agrup4,
footer, column_value, cursormoves1, layout_rel)
import traceback


def rel(nome_docu, dados, nip, nome):
    c, path = layout_rel(nome_docu)
    '''Dados será um orderdict derivado do query'''
    #manter tracking se já foi inserido o item uma vez para não repetir
    controle = dict()
    counter = []
    total_nf = 0
    total_ne = 0
    nav_ant = ''
    forn_ant = ''
    ne_ant = ''
    ne_equ_ant = False
    nav_equ_ant = False
    x = 1
    y = 22
    page = 0
    for rows in dados:
        if y <= 5.0:
            if page == 0:
                footer(c, nome, nip)
            c.showPage()
            c.setFont('Times-Roman', 12)
            y = 31
            page += 1
            footer(c, nome, nip)

        #navio

        if rows['nav'] not in controle:
           
            if ne_equ_ant == True:
                y -= 1
            c.setFont('Times-Bold', 12)
            y -= 1.3
            if page >= 1 and y == 22:
                y = 29
           
            y = nivel_agrup1(c, "Navio", rows['nav'], (x), (y))
            controle[rows['nav']] = [rows['nav']]
            c.line(x*cm, (y-0.3)*cm, 18*cm, (y-0.3)*cm)
            
        if nome_docu == 'Notas Fiscais Pagas':
            if rows['nav'] == nav_ant:
                nav_equ_ant = True
                y += 1
               
            else:
                nav_ant = rows['nav']
                nav_equ_ant = False
        else:
            if rows['nav'] == nav_ant:
                nav_equ_ant = True
            else:
                nav_ant = rows['nav']
                nav_equ_ant = False

        #fornecedor

        if rows['nome_fornecedor'] not in counter:
            if ne_equ_ant == True and nav_equ_ant == True:
                y -= 1
            c.setFont('Times-Bold', 12)
            y -= 0.3
            if page >= 1 and y ==22:
                y = 30
            
            y = nivel_agrup1(c, "Fornecedor", rows['nome_fornecedor'], (x+1), (y-1))
            controle[rows['nav']].append(rows['nome_fornecedor'])
            counter.append(rows['nome_fornecedor'])
            
        elif rows['nome_fornecedor'] not in controle[rows['nav']]:
            if ne_equ_ant == True and nav_equ_ant == True:
               y -= 1
            c.setFont('Times-Bold', 12)
            y -= 0.3
            if page >= 1 and y == 22:
                y = 30
            
            y = nivel_agrup1(c, "Fornecedor", rows['nome_fornecedor'], (x+1), (y-1))
            controle[rows['nav']].append(rows['nome_fornecedor'])

        try:

            if rows['nome_fornecedor'] == forn_ant and rows['nav'] == nav_ant and rows['n_ne'] not in counter:
                y -= 1
        except:
            pass

        if nome_docu == 'Notas Fiscais Pagas' or nome_docu == 'Notas de Empenho':
            if rows['nome_fornecedor'] == forn_ant and nav_equ_ant == True:
                forn_ant = rows['nome_fornecedor']
                y += 1                
            else:
                forn_ant = rows['nome_fornecedor']
        else:
            forn_ant = rows['nome_fornecedor']
        #NE

        try:

            try:
                
                if rows['n_ne'] not in counter:
                    y = nivel_agrup2(c, ['NE', 'Valor', 'Saldo', 'Data'], [rows['n_ne'], 'R$ {}'.format(rows['vl_ne']),
                    'R$ {}'.format(rows['disponivel']), rows['data_ne'].strftime("%d/%m/%y")], (x+1), (y-1), line=False, bold=False)
                    controle[rows['nav']].append(rows['n_ne'])
                    counter.append(rows['n_ne'])
                    ne_ant = rows['n_ne']
                   
                    
                elif rows['n_ne'] not in controle[rows['nav']]:
                   
                    y = nivel_agrup2(c, ['NE', 'Valor', 'Saldo', 'Data'], [rows['n_ne'], 'R$ {}'.format(rows['vl_ne']),
                    'R$ {}'.format(rows['disponivel']), rows['data_ne'].strftime("%d/%m/%y")], (x+1), (y-1), line=False, bold=False)
                    controle[rows['nav']].append(rows['n_ne'])
                    ne_ant = rows['n_ne']
                   
                    
                total_ne += rows['vl_ne']
            except:
                if rows['n_ne'] not in counter:
                   
                    y = nivel_agrup2(c, ['NE', 'Valor', 'Saldo'], [rows['n_ne'], 'R$ {}'.format(rows['vl_ne']),
                    'R$ {}'.format(rows['disponivel'])], (x+1), (y-1), line=True, bold=True)
                    controle[rows['nav']].append(rows['n_ne'])
                    counter.append(rows['n_ne'])
                    ne_ant = rows['n_ne']
                   
                elif rows['n_ne'] not in controle[rows['nav']]:
                    
                    
                    y = nivel_agrup2(c, ['NE', 'Valor', 'Saldo'], [rows['n_ne'], 'R$ {}'.format(rows['vl_ne']),
                    'R$ {}'.format(rows['disponivel'])], (x+1), (y-1), line=True, bold=True)
                    controle[rows['nav']].append(rows['n_ne'])
                    ne_ant = rows['n_ne']
                    
                total_ne += rows['vl_ne']
                
                pass

            
        except Exception:
            
            #traceback.print_exc()
            if nome_docu != 'Notas Fiscais Pagas':
                y -= 0.5 
            pass
        
        c.setFont('Times-Roman', 12)

        #NF

        try:
            if nome_docu == 'Notas Fiscais':
                total_nf += rows['vl_nf']
                y = nivel_agrup3(c, ['Nota Fiscal', 'Data', 'Valor', 'Data de pagamento'], 
                                [rows['n_nf'], rows['data_nf'].strftime("%d/%m/%y"), 
                                'R$ {}'.format(rows['vl_nf']), (rows['data_pg'].strftime("%d/%m/%y") if rows['data_pg'] is not None else rows['data_pg'])], (x+2.5), (y-1.5))
            else:
                total_nf += rows['vl_nf']
                y = nivel_agrup3(c, ['Nota Fiscal', 'Data', 'Valor', 'Data de pagamento'], 
                                    [rows['n_nf'], rows['data_nf'].strftime("%d/%m/%y"), 
                                    'R$ {}'.format(rows['vl_nf']), (rows['data_pg'].strftime("%d/%m/%y") if rows['data_pg'] is not None else rows['data_pg'])], (x+2.5), (y-1.0))
                
            if rows['nome_fornecedor'] == forn_ant and nome_docu == 'Notas Fiscais Pagas':
                y -= 1 

            if rows['n_ne'] == ne_ant:
                y += 1
                ne_equ_ant = True   
            else:
                ne_ant = rows['n_ne']
                ne_equ_ant = False
            

        except Exception:
            
            #traceback.print_exc()
            y -= 0.5
            pass
    
    if y <= 5 or (y>5 and page == 0):
        y = 6
        if total_nf != 0:
            y = nivel_agrup4(c, 'NF', 'R$ {}'.format(total_nf), y)
        elif total_ne != 0 and total_nf == 0:
            y = nivel_agrup4(c, 'NE', 'R$ {}'.format(total_ne), y)
            
        if page == 0:
            footer(c, nome, nip)
    else:
        if total_nf != 0:
            y = nivel_agrup4(c, 'NF', 'R$ {}'.format(total_nf), y)
        elif total_ne != 0 and total_nf == 0:
            y = nivel_agrup4(c, 'NE', 'R$ {}'.format(total_ne), y)

    c.showPage()
    c.save()

    return path

